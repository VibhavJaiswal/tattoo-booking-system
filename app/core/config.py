import os
from dotenv import load_dotenv
from pathlib import Path

# ✅ Ensures .env is loaded relative to project root, even when run from uvicorn
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
MODEL_PATH = os.getenv("MODEL_PATH")
CLASSIFIER_MODEL_PATH = os.getenv("CLASSIFIER_MODEL_PATH", "tattoo_classifier.pth")
GOOGLE_CALENDAR_CREDENTIALS = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

# Validate required keys
if not OPENAI_API_KEY:
    raise ValueError("❌ OpenAI API Key not found! Please add it to .env.")

if not API_SECRET_KEY:
    raise ValueError("❌ API_SECRET_KEY not found! Please add it to .env.")
