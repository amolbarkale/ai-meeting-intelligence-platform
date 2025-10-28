import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db import models, database
from app.api.v1 import schemas
from app.services.processing_service import process_meeting_file

router = APIRouter()

# Define the directory to store uploaded files
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

ALLOWED_EXTENSIONS = {".mp4", ".mp3", ".wav", ".m4a", ".avi", ".mov", ".mkv"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

@router.post("/upload", response_model=schemas.MeetingResponse, status_code=202)
def upload_meeting_file(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    """
    Upload an audio/video file for processing.
    The file is saved and a background task is triggered.
    """

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_extension} not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Generate a unique filename to avoid conflicts
    saved_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, saved_filename)

    # Save the uploaded file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Create a new meeting record in the database
    new_meeting = models.Meeting(
        original_filename=file.filename,
        saved_filename=saved_filename,
        file_path=file_path,
        status=models.MeetingStatus.PENDING
    )
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    # Trigger the background processing task
    process_meeting_file.delay(str(new_meeting.id))

    return new_meeting


@router.get("/{meeting_id}/status", response_model=schemas.JobStatusResponse)
def get_meeting_status(
    meeting_id: uuid.UUID,
    db: Session = Depends(database.get_db)
):
    """
    Check the processing status of a meeting.
    """
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return schemas.JobStatusResponse(
        meeting_id=meeting.id,
        status=meeting.status,
        message=f"Processing status for meeting {meeting.id} is {meeting.status.value}"
    )

@router.get("/{meeting_id}", response_model=schemas.MeetingDetailsResponse)
def get_meeting_details(
    meeting_id: uuid.UUID,
    db: Session = Depends(database.get_db)
):
    """
    Retrieve the full details, transcript, and summary of a processed meeting.
    """
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return meeting