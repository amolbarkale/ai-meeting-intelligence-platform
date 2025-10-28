from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import meetings, search 
from app.db import database, models
import os
import subprocess
import redis
from app.core.config import settings

# For production, use Alembic migrations
# models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="AI Meeting Intelligence Platform",
    description="Process meeting recordings to generate summaries and insights.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    meetings.router,
    prefix="/api/v1/meetings",
    tags=["Meetings"]
)

app.include_router(
    search.router,
    prefix="/api/v1/search",
    tags=["Search"]
)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the AI Meeting Intelligence Platform API"}

@app.get("/health", tags=["Health"])
def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "service": "ai-meeting-platform"}

@app.get("/ready", tags=["Health"])
def readiness_check():
    """Readiness check for dependencies"""
    checks = {}
    
    # Check database
    try:
        with database.SessionLocal() as db:
            db.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
    
    # Check Redis
    try:
        r = redis.from_url(settings.CELERY_BROKER_URL)
        r.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"
    
    # Check FFmpeg
    try:
        ffmpeg_path = getattr(settings, 'FFMPEG_PATH', 'ffmpeg')
        subprocess.run([ffmpeg_path, "-version"], capture_output=True, check=True)
        checks["ffmpeg"] = "ok"
    except Exception as e:
        checks["ffmpeg"] = f"error: {str(e)}"
    
    # Check Whisper.cpp
    try:
        if os.path.exists(settings.WHISPER_CPP_PATH):
            checks["whisper"] = "ok"
        else:
            checks["whisper"] = f"error: path not found: {settings.WHISPER_CPP_PATH}"
    except Exception as e:
        checks["whisper"] = f"error: {str(e)}"
    
    # Check if all critical services are ok
    critical_services = ["database", "redis", "ffmpeg", "whisper"]
    all_ok = all(checks.get(service, "").startswith("error") == False for service in critical_services)
    
    if not all_ok:
        raise HTTPException(status_code=503, detail={"status": "not ready", "checks": checks})
    
    return {"status": "ready", "checks": checks}