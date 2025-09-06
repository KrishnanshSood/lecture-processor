import asyncio
import os
from app.extractors import extract_text_from_pdf
from app.llm_client import GeminiLLMClient

async def process_pdf(pdf_path):
    print(f"Extracting text from PDF: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    print(f"Extracted {len(text)} characters from PDF.")

    llm = GeminiLLMClient()
    print("Generating summary...")
    summary = await llm.summarize(text)
    print("Summary:", summary)

    print("Generating flashcards...")
    flashcards = await llm.generate_flashcards(text)
    print("Flashcards:", flashcards)

if __name__ == "__main__":
    # Example usage: python process_pdf.py path/to/file.pdf
    import sys
    if len(sys.argv) < 2:
        print("Usage: python process_pdf.py <pdf_path>")
    else:
        asyncio.run(process_pdf(sys.argv[1]))
