import uuid
import os
import asyncio
import tempfile
import json
from .storage import upload_file_path, upload_fileobj
from .transcribe import extract_audio_from_video, DummyTranscriber, chunk_text
from .chunker import make_chunks
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
            tmp_dir = tempfile.gettempdir()
            tmp_audio = os.path.join(tmp_dir, f"{job_id}.wav")
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
            with open(path, "r", encoding="utf-8") as f:
                transcript = f.read()

        print(transcript[:500])  # preview first 500 chars

        # ✅ Save transcript to temp file
        tmp_dir = tempfile.gettempdir()
        transcript_path = os.path.join(tmp_dir, f"{job_id}_transcript.txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"[DEBUG] Transcript saved to {transcript_path}")

        # upload transcript if needed
        transcript_s3 = upload_file_path(transcript_path, f"transcripts/{job_id}.txt")
        job.transcript_s3_path = transcript_s3

        # 3) Chunk transcript
        chunks = chunk_text(transcript, max_tokens=400)

        # 4) Process chunks with LLM
        summary_parts, quizzes, flashcards = [], [], []
        localized = {}

        async def process_chunk(chunk_text):
            print("Calling LLM: summarize...")
            try:
                s = await llm_client.summarize(chunk_text)
                print("LLM summarize: success")
            except Exception as e:
                print(f"LLM summarize: failed: {e}")
                s = f"ERROR: {e}"

            print("Calling LLM: generate_quiz...")
            try:
                q = await llm_client.generate_quiz(chunk_text)
                print("LLM generate_quiz: success")
            except Exception as e:
                print(f"LLM generate_quiz: failed: {e}")
                q = [f"ERROR: {e}"]

            print("Calling LLM: generate_flashcards...")
            try:
                f = await llm_client.generate_flashcards(chunk_text)
                print("LLM generate_flashcards: success")
            except Exception as e:
                print(f"LLM generate_flashcards: failed: {e}")
                f = [f"ERROR: {e}"]

            return s, q, f

        tasks = [process_chunk(c) for c in chunks]
        chunk_results = await asyncio.gather(*tasks)
        for s, q, f in chunk_results:
            summary_parts.append(s)
            quizzes.extend(q)
            flashcards.extend(f)

        # 5) Final summary
        long_summary = "\n\n".join(summary_parts)
        summary_chunks = chunk_text(long_summary, max_tokens=400)
        compressed_parts = []
        print("Calling LLM: summarize (final_summary)...")
        for chunk in summary_chunks:
            try:
                compressed = await llm_client.summarize(chunk)
                print("LLM summarize (final_summary chunk): success")
            except Exception as e:
                print(f"LLM summarize (final_summary chunk): failed: {e}")
                compressed = f"ERROR: {e}"
            compressed_parts.append(compressed)
        final_summary = "\n\n".join(compressed_parts)

        # 6) Localization
        locales = locales or ["hi-IN"]
        for loc in locales:
            print(f"Calling LLM: localize to {loc}...")
            try:
                localized[loc] = await llm_client.localize(final_summary, loc)
                print(f"LLM localize to {loc}: success")
            except Exception as e:
                print(f"LLM localize to {loc}: failed: {e}")
                localized[loc] = f"ERROR: {e}"

        results = Results(
            summary=final_summary,
            quizzes=quizzes,
            flashcards=flashcards,
            localized=localized,
        )

        # 7) Save results JSON
        tmp_out = os.path.join(tmp_dir, f"{job_id}.json")
        with open(tmp_out, "w", encoding="utf-8") as f:
            json.dump(results.dict(), f, ensure_ascii=False, indent=2)
        print(f"[DEBUG] Results saved to {tmp_out}")

        s3_uri = upload_file_path(tmp_out, f"results/{job_id}.json")
        job.result_s3_path = s3_uri
        job.status = job.status.__class__.DONE
        return job

    except Exception as e:
        job.status = job.status.__class__.FAILED
        job.error = str(e)
        return job
