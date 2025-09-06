import requests
import os

# Load environment variables from .env if present
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

# Test file path (replace with a small file you have, e.g. lecture.mp4 or any .txt/.pdf)
TEST_FILE = "lecture.mp4"  # Change to a real file in your folder
API_URL = "http://localhost:8000/upload"

if not os.path.exists(TEST_FILE):
    print(f"Test file {TEST_FILE} not found. Please place a file named 'lecture.mp4' in the project root or update TEST_FILE.")
    exit(1)

with open(TEST_FILE, "rb") as f:
    files = {"file": (os.path.basename(TEST_FILE), f)}
    response = requests.post(API_URL, files=files)
    print("Upload response:", response.status_code, response.text)
