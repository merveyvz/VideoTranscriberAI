import os
from dotenv import load_dotenv


def load_config():
    load_dotenv()

    if 'OPENAI_API_KEY' not in os.environ:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
