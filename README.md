docker run -d -p 6379:6379 redis

docker stop container-id

uvicorn app.main:app --reload

celery -A worker.celery_app worker --loglevel=info -P eventlet

# AI Meeting Intelligence Platform - Backend

## Setup and Installation

Follow these steps to set up and run the backend services.

### 1. Prerequisites

- Python 3.10+
- Docker (for running Redis)
- Git

### 2. Initial Setup

1. **Clone the Repository:**
   ```bash
   git clone https://gitingest.com/amolbarkale/ai-meeting-intelligence-platform.git
   cd ai-meeting-intelligence-platform/backend
   ```

2. **Create and Activate Python Virtual Environment:**
   ```bash
   # For Windows
   python -m venv .venv
   .\.venv\Scripts\activate

   # For macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### 3. Install External Dependencies

The application relies on `ffmpeg` for audio processing and `whisper.cpp` for transcription.

1. **Install FFmpeg:**
   - **macOS (Homebrew):** `brew install ffmpeg`
   - **Linux (apt):** `sudo apt update && sudo apt install ffmpeg`
   - **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add the `bin` directory to your system's PATH.

2. **Build whisper.cpp and Download Model:**
   ```bash
   # Clone the repository
   git clone https://github.com/ggerganov/whisper.cpp.git

   # Build the executable
   cd whisper.cpp
   make

   # Download the 'base' model
   ./models/download-ggml-model.sh base

   # Return to the backend directory
   cd ..
   ```

### 4. Configure Environment

1. Create a `.env` file in the `backend` directory by copying the example:
   ```bash
   # (Create a .env.example file first for others to use)
   cp .env.example .env
   ```

2. Your `.env` file should contain:
   ```
   DATABASE_URL="sqlite:///./meetings.db"
   CELERY_BROKER_URL="redis://127.0.0.1:6379/0"
   CELERY_RESULT_BACKEND="redis://127.0.0.1:6379/0"
   WHISPER_CPP_PATH="./whisper.cpp/main"
   WHISPER_CPP_MODEL_PATH="./whisper.cpp/models/ggml-base.bin"
   ```

### 5. Initialize the Database

Run the database creation script once to set up your `meetings.db` file:
```bash
python create_db.py
```