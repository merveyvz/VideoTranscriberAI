import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

SUPPORTED_LANGUAGES = ["English", "Turkish", "French", "German", "Spanish", "Italian"]

WHISPER_MODEL = "whisper-1"
GPT_MODEL = "gpt-4o-mini"

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)
