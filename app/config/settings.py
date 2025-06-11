import os
from dotenv import load_dotenv

# Load .env file if it exists (for local, non-Docker development)
load_dotenv()

# --------- Shared Application Settings ------------

# Read from environment, with sensible defaults for local development
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8001))

# --------- API Keys -----------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # TODO: configure gemini api key, replace LLM