class BaseLLMClient:
	async def summarize(self, text: str) -> str:
		raise NotImplementedError()

	async def generate_quiz(self, text: str) -> List[Dict]:
		raise NotImplementedError()

	async def generate_flashcards(self, text: str) -> List[Dict]:
		raise NotImplementedError()

	async def localize(self, text: str, locale: str) -> str:
		raise NotImplementedError()
import os
from typing import List, Dict
import openai


class OpenAILLMClient(BaseLLMClient):
	def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
		self.api_key = api_key or os.getenv("OPENAI_API_KEY")
		self.model = model
		openai.api_key = self.api_key

	async def summarize(self, text: str) -> str:
		prompt = f"Summarize the following educational content concisely for learners.\n\n{text}"
		return await self._run_openai(prompt)

	async def generate_quiz(self, text: str) -> List[Dict]:
		prompt = (
			"Create 5 multiple-choice questions from the following text. "
			"For each question, provide: question, 4 options, and the correct option index. "
			"Return as JSON array.\n\n" + text
		)
		out = await self._run_openai(prompt)
		return [{"raw": out}]

	async def generate_flashcards(self, text: str) -> List[Dict]:
		prompt = (
			"Create 5 flashcards from the following text. "
			"Each flashcard should have a question and an answer. "
			"Return as JSON array.\n\n" + text
		)
		out = await self._run_openai(prompt)
		return [{"raw": out}]

	async def localize(self, text: str, locale: str) -> str:
		prompt = (
			f"Localize the following content to {locale}. Adapt tone for learners.\n\n{text}"
		)
		return await self._run_openai(prompt)

	async def _run_openai(self, prompt: str) -> str:
		import asyncio
		def run():
			response = openai.ChatCompletion.create(
				model=self.model,
				messages=[{"role": "user", "content": prompt}],
				max_tokens=400
			)
			return response["choices"][0]["message"]["content"].strip()
		return await asyncio.to_thread(run)
