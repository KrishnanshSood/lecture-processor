from typing import List
import ffmpeg

def extract_audio_from_video(video_path: str, out_path: str, sample_rate=16000):
    # using ffmpeg-python to convert to wav
    stream = ffmpeg.input(video_path)
    stream = ffmpeg.output(stream, out_path, ar=sample_rate, ac=1)
    ffmpeg.run(stream, overwrite_output=True)
    return out_path
def chunk_text(text: str, max_tokens: int = 800) -> List[str]:
    """Very simple chunk by approx chars (tune to tokens for your LLM)."""
    avg_chars_per_token = 4
    max_chars = max_tokens * avg_chars_per_token
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i: i + max_chars]
        # try to cut at sentence boundary
        last_period = chunk.rfind(". ")
        if last_period > int(max_chars * 0.6):
            chunk = chunk[: last_period + 1]
            i += last_period + 1
        else:
            i += max_chars
        chunks.append(chunk.strip())
    return chunks


from typing import List

class BaseTranscriber:
    async def transcribe(self, audio_path: str) -> str:
        """Return full transcript as string"""
        raise NotImplementedError()

class DummyTranscriber(BaseTranscriber):
    async def transcribe(self, audio_path: str) -> str:
        # placeholder for testing
        return "This is a dummy transcript of the lecture audio. Replace with real transcriber."
