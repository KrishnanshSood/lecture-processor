
import os
from typing import List, Dict
import asyncio

class BaseLLMClient:
    async def summarize(self, text: str) -> str:
        raise NotImplementedError()

    async def generate_quiz(self, text: str) -> List[Dict]:
        raise NotImplementedError()

    async def generate_flashcards(self, text: str) -> List[Dict]:
        raise NotImplementedError()

    async def localize(self, text: str, locale: str) -> str:
        raise NotImplementedError()

# Dummy LLM client for local testing
class DummyLLMClient(BaseLLMClient):
    async def summarize(self, text: str) -> str:
        return "This is a dummy summary."

    async def generate_quiz(self, text: str) -> List[Dict]:
        return [
            {"question": "What is a dummy question?", "options": ["A", "B", "C", "D"], "answer": 0}
        ]

    async def generate_flashcards(self, text: str) -> List[Dict]:
        return [
            {"question": "Dummy flashcard Q?", "answer": "Dummy flashcard A."}
        ]

    async def localize(self, text: str, locale: str) -> str:
        return f"[Localized to {locale}]: {text}"



    async def localize(self, text: str, locale: str) -> str:
        raise NotImplementedError()


# Example OpenAI-based implementation (synchronous calls; wrap in threadpool for production)

import os
from typing import List, Dict

class BaseLLMClient:
    async def summarize(self, text: str) -> str:
        raise NotImplementedError()

    async def generate_quiz(self, text: str) -> List[Dict]:
        raise NotImplementedError()

    async def localize(self, text: str, locale: str) -> str:
        raise NotImplementedError()

# Gemini implementation
import google.generativeai as genai



class GeminiLLMClient(BaseLLMClient):
    def __init__(self, api_key: str = None, model: str = "models/gemini-1.5-pro-latest"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        genai.configure(api_key=self.api_key)
        self.model_obj = genai.GenerativeModel(self.model)

    async def summarize(self, text: str) -> str:
        prompt = f"Summarize the following educational content concisely for learners.\n\n{text}"
        response = await asyncio.to_thread(self.model_obj.generate_content, prompt)
        return response.text.strip() if hasattr(response, 'text') else str(response)

    async def generate_quiz(self, text: str) -> List[Dict]:
        prompt = (
            "Create 5 multiple-choice questions from the following text. "
            "For each question, provide: question, 4 options, and the correct option index. "
            "Return as JSON array.\n\n" + text
        )
        response = await asyncio.to_thread(self.model_obj.generate_content, prompt)
        out = response.text.strip() if hasattr(response, 'text') else str(response)
        return [{"raw": out}]

    async def generate_flashcards(self, text: str) -> List[Dict]:
        prompt = (
            "Create 5 flashcards from the following text. "
            "Each flashcard should have a question and an answer. "
            "Return as JSON array.\n\n" + text
        )
        response = await asyncio.to_thread(self.model_obj.generate_content, prompt)
        out = response.text.strip() if hasattr(response, 'text') else str(response)
        return [{"raw": out}]

    async def localize(self, text: str, locale: str) -> str:
        prompt = (
            f"Localize the following content to {locale}. Adapt tone for learners.\n\n{text}"
        )
        response = await asyncio.to_thread(self.model_obj.generate_content, prompt)
        return response.text.strip() if hasattr(response, 'text') else str(response)
