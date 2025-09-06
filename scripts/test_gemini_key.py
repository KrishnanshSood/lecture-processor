import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env to get the API key
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    response = model.generate_content("Say hello world!")
    print("Gemini API test response:", response.text)
except Exception as e:
    print("Gemini API test error:", e)
