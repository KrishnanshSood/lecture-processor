import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env to get the API key
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)
api_key = os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=api_key)

print('Available Gemini models:')
for model in genai.list_models():
    print(model.name)
