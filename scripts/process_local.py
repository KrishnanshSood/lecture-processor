print("[DEBUG] Script started: process_local.py")

import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
import asyncio
from app.pipeline import process_file_local
from app.llm_client import GeminiLLMClient
from app.transcribe import DummyTranscriber

async def main():
    print("[DEBUG] Starting main() in process_local.py")
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(project_root, "lecture.mp4")
    print(f"[DEBUG] Checking for lecture.mp4: Exists={os.path.exists(path)} | Path={path}")

    # Extract only the first 10 seconds of audio for testing
    import ffmpeg
    short_audio_path = os.path.join(project_root, "lecture_10s.wav")
    try:
        (
            ffmpeg
            .input(path, t=10)
            .output(short_audio_path, ar=16000, ac=1)
            .overwrite_output()
            .run()
        )
        print(f"[DEBUG] Created short audio: {short_audio_path}")
    except Exception as e:
        print(f"[ERROR] ffmpeg failed: {e}")

    from app.llm_client import GeminiLLMClient
    llm = GeminiLLMClient()
    trans = DummyTranscriber()
    print("[DEBUG] Starting process_file_local...")
    try:
        job = await process_file_local(short_audio_path, "lecture_10s.wav", llm, trans, ["hi-IN"])
        print(f"[DEBUG] Job result: {job}")
    except Exception as e:
        print(f"[ERROR] process_file_local failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
