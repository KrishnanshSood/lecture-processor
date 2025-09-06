import uuid
import os
import asyncio
import json
from .transcribe import extract_audio_from_video, DummyTranscriber, chunk_text
from .llm_client import BaseLLMClient
from .models import Job, Results


async def process_file_local(path: str, filename: str, llm_client: BaseLLMClient, transcriber=None, locales=None):
    job_id = str(uuid.uuid4())
    job = Job(job_id=job_id, filename=filename)
    job.status = job.status.__class__.PENDING

    try:
        job.status = job.status.__class__.PROCESSING

        # 1) If video, extract audio
        ext = os.path.splitext(filename)[1].lower()
        audio_path = None
        if ext in [".mp4", ".mov", ".mkv", ".avi"]:
            transcripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "transcripts")
            os.makedirs(transcripts_dir, exist_ok=True)
            tmp_audio = os.path.join(transcripts_dir, f"{job_id}.wav")
            extract_audio_from_video(path, tmp_audio)
            audio_path = tmp_audio
        elif ext in [".mp3", ".wav"]:
            audio_path = path
        else:
            audio_path = None

        # 2) Transcribe
        transcriber = transcriber or DummyTranscriber()
        if audio_path:
            transcript = await transcriber.transcribe(audio_path)
        else:
            # For ppt/pdf, extract text (not implemented here)
            with open(path, "r", encoding="utf-8") as f:
                transcript = f.read()

        # Save transcript into transcripts/ folder
        transcripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "transcripts")
        os.makedirs(transcripts_dir, exist_ok=True)
        transcript_path = os.path.join(transcripts_dir, f"{job_id}_transcript.txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"[DEBUG] Transcript saved to {transcript_path}")

        # 3) Chunk transcript
        chunks = chunk_text(transcript, max_tokens=400)

        # 4) Run LLM tasks per chunk
        summary_parts = []
        quizzes = []
        flashcards = []
        localized = {}

        async def process_chunk(chunk_text):
            try:
                s = await llm_client.summarize(chunk_text)
            except Exception as e:
                s = f"ERROR: {e}"

            try:
                q = await llm_client.generate_quiz(chunk_text)
            except Exception as e:
                q = [f"ERROR: {e}"]

            try:
                f = await llm_client.generate_flashcards(chunk_text)
            except Exception as e:
                f = [f"ERROR: {e}"]

            return s, q, f

        tasks = [process_chunk(c) for c in chunks]
        chunk_results = await asyncio.gather(*tasks)
        for s, q, f in chunk_results:
            summary_parts.append(s)
            quizzes.extend(q)
            flashcards.extend(f)

        # 5) Compose final summary
        long_summary = "\n\n".join(summary_parts)
        summary_chunks = chunk_text(long_summary, max_tokens=400)
        compressed_parts = []
        for chunk in summary_chunks:
            try:
                compressed = await llm_client.summarize(chunk)
            except Exception as e:
                compressed = f"ERROR: {e}"
            compressed_parts.append(compressed)
        final_summary = "\n\n".join(compressed_parts)

        # 6) Localization
        locales = locales or ["hi-IN"]
        for loc in locales:
            try:
                localized[loc] = await llm_client.localize(final_summary, loc)
            except Exception as e:
                localized[loc] = f"ERROR: {e}"

        results = Results(
            summary=final_summary,
            quizzes=quizzes,
            flashcards=flashcards,
            localized=localized,
        )

        # 7) Save results into transcripts/ folder
        results_path = os.path.join(transcripts_dir, f"{job_id}_results.json")
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results.dict(), f, ensure_ascii=False, indent=2)
        print(f"[DEBUG] Results saved to {results_path}")

        job.result_s3_path = results_path
        job.status = job.status.__class__.DONE
        return job

    except Exception as e:
        job.status = job.status.__class__.FAILED
        job.error = str(e)
        return job
