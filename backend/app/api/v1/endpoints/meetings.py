import os
import uuid
import shutil
import logging
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import models, database
from app.api.v1 import schemas
from app.services.processing_service import process_meeting_file
from app.services.graph_service import fetch_meeting_context, upsert_meeting_graph
from app.services.llm_service import generate_meeting_chat_response
from kombu.exceptions import OperationalError

logger = logging.getLogger(__name__)

router = APIRouter()

# Define the directory to store uploaded files (use absolute path)
# Get the backend directory (parent of app directory)
# __file__ is at: backend/app/api/v1/endpoints/meetings.py
# We need to go up 4 levels to get to backend/
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
UPLOAD_DIRECTORY = os.path.join(BACKEND_DIR, "uploads")
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
logger.info(f"Upload directory set to: {UPLOAD_DIRECTORY}")

ALLOWED_EXTENSIONS = {".mp4", ".mp3", ".wav", ".m4a", ".avi", ".mov", ".mkv"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


def _split_tags(tags: Optional[str]) -> List[str]:
    if not tags:
        return []
    return [tag.strip() for tag in tags.split(",") if tag.strip()]


@router.get("", response_model=List[schemas.MeetingResponse])
def list_meetings(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of meetings to return"),
    status: Optional[models.MeetingStatus] = Query(None, description="Optional status filter"),
    db: Session = Depends(database.get_db)
):
    """Return recent meetings with optional status filtering."""
    query = db.query(models.Meeting).order_by(models.Meeting.created_at.desc())

    if status:
        query = query.filter(models.Meeting.status == status)

    meetings = query.limit(limit).all()

    for meeting in meetings:
        try:
            upsert_meeting_graph(
                {
                    "id": str(meeting.id),
                    "original_filename": meeting.original_filename,
                    "saved_filename": meeting.saved_filename,
                    "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
                    "updated_at": meeting.updated_at.isoformat() if meeting.updated_at else None,
                    "status": meeting.status.value if meeting.status else None,
                    "summary": meeting.summary,
                    "key_points": meeting.key_points,
                    "action_items": meeting.action_items,
                    "sentiment": meeting.sentiment,
                    "tags": meeting.tags,
                    "transcript": meeting.transcript,
                    "knowledge_graph": meeting.knowledge_graph,
                }
            )
        except Exception as sync_exc:
            logger.debug("Skipping graph sync for meeting %s: %s", meeting.id, sync_exc)
    return meetings


@router.post("/upload", response_model=schemas.MeetingResponse, status_code=202)
def upload_meeting_file(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    """
    Upload an audio/video file for processing.
    The file is saved and a background task is triggered.
    """
    try:
        logger.info(f"Received upload request for file: {file.filename}")
        
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
        
        logger.info(f"File size: {file_size} bytes")
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
    # Generate a unique filename to avoid conflicts
        saved_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, saved_filename)
        
        logger.info(f"Saving file to: {file_path}")

    # Save the uploaded file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            logger.info(f"File saved successfully: {file_path}")
    except Exception as e:
            logger.error(f"Failed to save file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Create a new meeting record in the database
        try:
    new_meeting = models.Meeting(
        original_filename=file.filename,
        saved_filename=saved_filename,
        file_path=file_path,
        status=models.MeetingStatus.PENDING
    )
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)
            logger.info(f"Created meeting record with id: {new_meeting.id}")
        except Exception as e:
            logger.error(f"Failed to create meeting record: {e}", exc_info=True)
            # Clean up saved file if database operation fails
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Failed to create meeting record: {e}")

    # Trigger the background processing task
        try:
            logger.info(f"Queuing processing task for meeting {new_meeting.id}")
            # Use delay() which should return immediately even if worker is not running
            task_result = process_meeting_file.delay(str(new_meeting.id))
            logger.info(f"Successfully queued processing task for meeting {new_meeting.id}, task_id: {task_result.id}")
        except (OperationalError, ConnectionError) as e:
            logger.error(f"Failed to queue processing task (Redis/Celery error) for meeting {new_meeting.id}: {e}", exc_info=True)
            # Update meeting status to indicate task queue failure
            new_meeting.status = models.MeetingStatus.FAILED
            db.commit()
            raise HTTPException(
                status_code=503,
                detail=f"Failed to queue processing task. Please ensure Redis is running and Celery worker is started. Error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error queuing processing task for meeting {new_meeting.id}: {e}", exc_info=True)
            new_meeting.status = models.MeetingStatus.FAILED
            db.commit()
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error queuing processing task: {str(e)}"
            )

        logger.info(f"Upload completed successfully for meeting {new_meeting.id}")
    return new_meeting
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{meeting_id}/graph", response_model=schemas.GraphContextResponse)
def get_meeting_graph_context(
    meeting_id: uuid.UUID,
    db: Session = Depends(database.get_db),
):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    context = fetch_meeting_context(str(meeting.id))
    if not context:
        try:
            upsert_meeting_graph(
                {
                    "id": str(meeting.id),
                    "original_filename": meeting.original_filename,
                    "saved_filename": meeting.saved_filename,
                    "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
                    "updated_at": meeting.updated_at.isoformat() if meeting.updated_at else None,
                    "status": meeting.status.value if meeting.status else None,
                    "summary": meeting.summary,
                    "key_points": meeting.key_points,
                    "action_items": meeting.action_items,
                    "sentiment": meeting.sentiment,
                    "tags": meeting.tags,
                    "transcript": meeting.transcript,
                    "knowledge_graph": meeting.knowledge_graph,
                }
            )
            context = fetch_meeting_context(str(meeting.id))
        except Exception as exc:
            logger.error("Failed to sync meeting %s to graph: %s", meeting_id, exc, exc_info=True)
            context = {}

    if context is None:
        raise HTTPException(status_code=404, detail="Graph context unavailable")

    tag_list = context.get("tags") or _split_tags(meeting.tags)
    title_candidate = context.get("title")
    if not title_candidate and meeting.summary:
        first_line = meeting.summary.splitlines()[0]
        if first_line.startswith("#"):
            title_candidate = first_line.lstrip("#").strip()

    return schemas.GraphContextResponse(
        meeting_id=meeting.id,
        summary=context.get("summary") or meeting.summary,
        key_points=meeting.key_points,
        action_items=meeting.action_items,
        sentiment=context.get("sentiment") or meeting.sentiment,
        tags=tag_list or [],
        topics=context.get("topics") or [],
        participants=context.get("participants") or [],
        decisions=context.get("decisions") or [],
        timeline=context.get("timeline") or [],
        key_points_structured=context.get("key_points_structured") or [],
        action_items_structured=context.get("action_items_structured") or [],
        concepts=context.get("concepts") or [],
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
        title=title_candidate or meeting.original_filename,
    )


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


@router.post("/{meeting_id}/chat", response_model=schemas.MeetingChatResponse)
def chat_about_meeting(
    meeting_id: uuid.UUID,
    payload: schemas.MeetingChatRequest,
    db: Session = Depends(database.get_db),
):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    context = fetch_meeting_context(str(meeting.id))
    if not context:
        try:
            upsert_meeting_graph(
                {
                    "id": str(meeting.id),
                    "original_filename": meeting.original_filename,
                    "saved_filename": meeting.saved_filename,
                    "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
                    "updated_at": meeting.updated_at.isoformat() if meeting.updated_at else None,
                    "status": meeting.status.value if meeting.status else None,
                    "summary": meeting.summary,
                    "key_points": meeting.key_points,
                    "action_items": meeting.action_items,
                    "sentiment": meeting.sentiment,
                    "tags": meeting.tags,
                    "transcript": meeting.transcript,
                    "knowledge_graph": meeting.knowledge_graph,
                }
            )
            context = fetch_meeting_context(str(meeting.id))
        except Exception as exc:
            logger.error("Failed to sync meeting %s to graph: %s", meeting_id, exc, exc_info=True)
            context = {}
    else:
        context = context or {}

    # Merge SQL context to ensure we have fallbacks
    context.setdefault("original_filename", meeting.original_filename)
    context.setdefault("created_at", meeting.created_at.isoformat() if meeting.created_at else None)
    context.setdefault("summary", meeting.summary)
    context.setdefault("key_points_markdown", meeting.key_points)
    context.setdefault("action_items_markdown", meeting.action_items)
    context.setdefault("sentiment", meeting.sentiment)
    context.setdefault("tags", context.get("tags") or _split_tags(meeting.tags))
    context.setdefault("topics", context.get("topics") or [])
    context.setdefault("participants", context.get("participants") or [])
    context.setdefault("decisions", context.get("decisions") or [])
    context.setdefault("timeline", context.get("timeline") or [])
    context.setdefault("concepts", context.get("concepts") or [])
    context.setdefault("key_points_structured", context.get("key_points_structured") or [])
    context.setdefault("action_items_structured", context.get("action_items_structured") or [])

    if not context.get("title"):
        title_candidate = None
        if meeting.summary:
            first_line = meeting.summary.splitlines()[0]
            if first_line.startswith("#"):
                title_candidate = first_line.lstrip("#").strip()
        context["title"] = title_candidate or meeting.original_filename

    try:
        reply = generate_meeting_chat_response(
            question=payload.message,
            meeting_context=context,
            history=[msg.model_dump() for msg in payload.history] if payload.history else [],
        )
    except Exception as exc:
        logger.error("Failed to generate chat response for meeting %s: %s", meeting_id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate chat response")

    return schemas.MeetingChatResponse(
        meeting_id=meeting.id,
        reply=reply,
        context={
            "title": context.get("title"),
            "tags": context.get("tags"),
            "created_at": context.get("created_at"),
            "topics": context.get("topics"),
            "participants": context.get("participants"),
            "decisions": context.get("decisions"),
            "timeline": context.get("timeline"),
        },
    )