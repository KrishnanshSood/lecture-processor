from typing import List


def make_chunks(transcript: str, chunk_size_chars: int = 4000):
    # Simple paragraph-based chunker
    paras = [p for p in transcript.split('\n') if p.strip()]
    chunks = []
    cur = []
    cur_len = 0
    for p in paras:
        if cur_len + len(p) > chunk_size_chars:
            chunks.append('\n'.join(cur))
            cur = [p]
            cur_len = len(p)
        else:
            cur.append(p)
            cur_len += len(p)
    if cur:
        chunks.append('\n'.join(cur))
    return chunks
