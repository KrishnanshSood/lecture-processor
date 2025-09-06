from pydantic import BaseModel
from enum import Enum
from typing import Optional, List, Dict

class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"

class Job(BaseModel):
    job_id: str
    filename: str
    status: JobStatus = JobStatus.PENDING
    result_s3_path: Optional[str] = None
    error: Optional[str] = None

class Chunk(BaseModel):
    id: int
    text: str

class Results(BaseModel):
    summary: str
    quizzes: List[Dict]
    flashcards: List[Dict]
    localized: Dict[str, str]  # language -> localized summary (or full payload)
