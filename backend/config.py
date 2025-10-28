import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "meetings.db"

# Create directories
UPLOAD_DIR.mkdir(exist_ok=True)

# AI Models
WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large
OLLAMA_MODEL = "mistral"  # Local Ollama model
OLLAMA_BASE_URL = "http://localhost:11434"

# Processing
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
SUPPORTED_FORMATS = [".mp3", ".wav", ".m4a", ".mp4", ".webm"]
