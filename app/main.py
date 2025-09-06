from fastapi import FastAPI, UploadFile, File, BackgroundTasks
import uuid
import os
from .pipeline import process_file_local
from .llm_client import GeminiLLMClient
from .transcribe import DummyTranscriber

app = FastAPI()

LLM = GeminiLLMClient()
TRANSCRIBER = DummyTranscriber()

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    job_id = str(uuid.uuid4())
    out_path = os.path.join(UPLOAD_DIR, f"{job_id}-{file.filename}")
    with open(out_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # enqueue background processing
    background_tasks.add_task(process_file_local, out_path, file.filename, LLM, TRANSCRIBER, ["hi-IN", "es-ES"])
    return {"job_id": job_id, "status": "queued"}

@app.get("/health")
async def health():
    return {"status": "ok"}
