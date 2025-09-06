
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
import asyncio
from app.pipeline import process_file_local
from app.llm_client import GeminiLLMClient
from app.transcribe import DummyTranscriber

async def main():
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(project_root, "lecture.mp4")
    print(f"File exists: {os.path.exists(path)} | Path: {path}")

    # Extract only the first 10 seconds of audio for testing
    import ffmpeg
    short_audio_path = os.path.join(project_root, "lecture_10s.wav")
    (
        ffmpeg
        .input(path, t=10)
        .output(short_audio_path, ar=16000, ac=1)
        .overwrite_output()
        .run()
    )
    print(f"Created short audio: {short_audio_path}")

    from app.llm_client import DummyLLMClient
    llm = DummyLLMClient()
    trans = DummyTranscriber()
    job = await process_file_local(short_audio_path, "lecture_10s.wav", llm, trans, ["hi-IN"])
    print(job)

if __name__ == "__main__":
    asyncio.run(main())
