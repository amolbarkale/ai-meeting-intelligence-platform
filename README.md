# AI Meeting Intelligence Platform

Process pre-recorded meeting audio/video to generate high-quality transcripts, summaries, insights, and searchable knowledge.

> 📋 **[Technical Documentation](docs/technical-overview.md)** - Comprehensive architecture analysis, AI pipeline implementation, and engineering challenges

## Tech Stack
- Backend: FastAPI, Celery, Redis, SQLAlchemy (SQLite)
- AI: Whisper.cpp (transcription), Pyannote (diarization), FFmpeg, Ollama/OpenAI (LLM), Chroma (vector search)
- Frontend: React + Tailwind (Next.js)

## Quick Start (TL;DR)
```bash
# 1) Start Redis (Docker)
docker run -d -p 6379:6379 redis

# 2) Backend (from backend/)
python -m venv .venv && . ./.venv/Scripts/activate  # Windows
# python3 -m venv .venv && source .venv/bin/activate # macOS/Linux
pip install -r requirements.txt

# 3) FFmpeg + Whisper.cpp (see detailed setup below)

# 4) Env
copy .env.example .env  # then fill values

# 5) Run services
uvicorn app.main:app --reload
celery -A worker.celery_app worker --loglevel=info -P eventlet

# 6) Open API docs
# http://127.0.0.1:8000/docs
```

---

## Backend: Setup & Run

### 1) Prerequisites
- Python 3.10+
- Docker Desktop (for Redis)
- Git

### 2) Create venv and install deps
```bash
cd backend
python -m venv .venv && . ./.venv/Scripts/activate  # Windows
# python3 -m venv .venv && source .venv/bin/activate # macOS/Linux
pip install --upgrade pip
pip install -r requirements.txt
```

### 3) External tools
- FFmpeg is required for audio preprocessing
  - Windows: download from `https://ffmpeg.org/download.html` and ensure `ffmpeg.exe` is available, or set `FFMPEG_PATH` in `.env`.
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt update && sudo apt install ffmpeg`

- Whisper.cpp for transcription
  - Windows: follow `backend/SETUP_WHISPER.md` for prebuilt binaries and model download
  - macOS/Linux (source build):
    ```bash
    git clone https://github.com/ggerganov/whisper.cpp.git
    cd whisper.cpp && make
    ./models/download-ggml-model.sh base
    ```

### 4) Environment variables
Create `backend/.env` (use `.env.example` as a guide):
```bash
DATABASE_URL=sqlite:///./meetings.db
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

# FFmpeg
FFMPEG_PATH=./ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe    # Windows example

# Whisper.cpp binary + model
WHISPER_CPP_PATH=./whisper.cpp/Release/main.exe                 # Windows example
WHISPER_CPP_MODEL_PATH=./ggml-base.bin                          # or ./whisper.cpp/models/ggml-base.bin

# Diarization (optional; enables Pyannote)
HF_TOKEN=your_huggingface_token

# LLMs
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:1b
OPENAI_API_KEY=your_openai_key

# Chroma (vector store) path
CHROMA_DB_PATH=./chroma_langchain_db
```

Fail-fast checks are available at:
- Health: `GET /health`
- Readiness: `GET /ready` (checks DB, Redis, FFmpeg, Whisper.cpp path)

### 5) Start infrastructure
```bash
# Redis
docker run -d -p 6379:6379 redis

# Stop later (find container ID first)
docker ps
docker stop <container-id>
```

### 6) Run backend services
In two terminals (with `backend/.venv` activated):
```bash
# API
uvicorn app.main:app --reload --port 8000

# Celery worker
celery -A worker.celery_app worker --loglevel=info -P eventlet
```

### 7) Initialize database (first run)
```bash
python -c "from app.db import models, database; models.Base.metadata.create_all(bind=database.engine)"
```

### 8) Test
- Open Swagger UI: `http://127.0.0.1:8000/docs`
- Upload endpoint: `POST /api/v1/meetings/upload` (accepts .mp4/.mp3/.wav/.m4a/.avi/.mov/.mkv, ≤100MB)
- Status: `GET /api/v1/meetings/{id}/status`
- Details: `GET /api/v1/meetings/{id}`
- Search: `GET /api/v1/search?query=...&top_k=5`

Notes:
- If `HF_TOKEN` is not set, diarization is skipped and speakers are marked `UNKNOWN_SPEAKER`.
- If Ollama/OpenAI are unavailable, insight generation may fail; the task auto-retries.

---

## Frontend: Setup & Run
```bash
cd frontend
npm install
npm run dev
# http://localhost:3000
```

---

## Whisper, FFmpeg, Tokens, and Keys

### FFmpeg
Ensure `ffmpeg` is installed and on PATH, or set `FFMPEG_PATH` in `.env`.

### Whisper.cpp
See `backend/SETUP_WHISPER.md` for Windows prebuilt setup, model downloads, and verification commands.

### Hugging Face Token (Pyannote)
Set `HF_TOKEN` in `.env` to enable diarization. Without it, diarization is skipped gracefully.

### OpenAI API Key
Set `OPENAI_API_KEY` to enable OpenAI embeddings via LangChain. Chunks are stored in Chroma at `CHROMA_DB_PATH`.

---

## API Overview
- Ingestion: `POST /api/v1/meetings/upload`
- Status: `GET /api/v1/meetings/{id}/status`
- Details: `GET /api/v1/meetings/{id}`
- Search: `GET /api/v1/search?query=...&top_k=5`
- Health: `GET /health`
- Ready: `GET /ready`

---

## Operational Tips
- Logs: Celery logs pipeline progress; FastAPI logs requests and health checks.
- Storage: Uploaded files are stored under `backend/uploads/`.
- Rate limits: Consider limiting large uploads and embedding throughput for production.

---

## Alternative: Deepgram for STT and Diarization
You may opt to use Deepgram’s APIs for speech-to-text and diarization as a managed alternative to local Whisper.cpp + Pyannote. This can reduce setup complexity and improve scale. See Deepgram’s site: [Deepgram Voice AI Platform](https://deepgram.com/).

---

## Project Scripts (reference)
```bash
# Start Redis (Docker)
docker run -d -p 6379:6379 redis

# Stop container (find ID first with: docker ps)
docker stop container-id

# Run FastAPI (from backend/)
uvicorn app.main:app --reload

# Run Celery worker (from backend/)
celery -A worker.celery_app worker --loglevel=info -P eventlet
```

---

## Troubleshooting
- `/ready` returns 503: verify Redis is running, FFmpeg is installed, Whisper paths exist.
- Upload fails: verify file extension and ensure file size ≤ 100MB.
- Insights fail: ensure Ollama is running and `OLLAMA_MODEL` is available, or set `OPENAI_API_KEY`.

---