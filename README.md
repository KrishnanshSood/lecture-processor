# Lecture Processor — Python codebase

This repository is a ready-to-run, modular Python codebase that implements the workflow in your diagram:

* Upload video lectures, PPTs, PDFs via an HTTP endpoint or a watch-folder
* Upload file to S3
* Extract audio from video / convert PPT -> text and PDF -> text
* Transcribe audio into text (chunked)
* Chunk transcript for LLM tasks
* Run three LLM tasks in parallel: Summarize, Quiz generation, Localization (translate + adapt)
* Merge outputs and store results back to S3

The code is intentionally modular so you can swap the transcription engine or LLM provider.

---

## Project structure

```
lecture-processor/
├── app/
│   ├── main.py                # FastAPI app for uploads and status
│   ├── pipeline.py            # Orchestrates the processing pipeline
│   ├── workers.py             # Background worker functions
│   ├── transcribe.py          # Transcription helpers (ffmpeg audio extraction + transcriber interface)
│   ├── llm_client.py          # Abstract LLM client + example OpenAI implementation
│   ├── chunker.py            # Transcript chunking utilities
│   ├── storage.py             # S3 upload/download helpers
│   ├── extractors.py         # PDF/PPT text extractors
│   └── models.py             # pydantic models (Job, Status, Results)
├── scripts/
│   └── process_local.py      # CLI for processing a local file (for testing)
├── Dockerfile
├── requirements.txt
└── README.md
```

---

See the code for usage and extension notes.
