import time
import logging
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Meeting, MeetingStatus
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from worker import celery_app

@celery_app.task(name="process_meeting_file")
def process_meeting_file(meeting_id: str):
    """
    Celery task to process an uploaded meeting file.
    This is the core AI pipeline.
    """
    logger.info(f"Starting processing for meeting_id: {meeting_id}")
    
    db: Session = SessionLocal()
    try:
        meeting = db.query(Meeting).filter(Meeting.id == uuid.UUID(meeting_id)).first()
        if not meeting:
            logger.error(f"Meeting with id {meeting_id} not found.")
            return

        # 1. Update status to PROCESSING
        meeting.status = MeetingStatus.PROCESSING
        db.commit()
        logger.info(f"Status updated to PROCESSING for meeting {meeting_id}")

        # === STUB AI PIPELINE ===
        # In the future, this is where we will call Whisper, Ollama, etc.
        
        # Step 2: Simulate transcription
        logger.info("Simulating transcription...")
        time.sleep(15) # Simulate a 15-second transcription job
        meeting.transcript = "This is a dummy transcript from the simulated AI pipeline."
        db.commit()

        # Step 3: Simulate summarization
        logger.info("Simulating summarization...")
        time.sleep(10) # Simulate a 10-second summarization job
        meeting.summary = "This is a dummy summary with key action items."
        db.commit()
        
        # === END STUB AI PIPELINE ===

        # 4. Update status to COMPLETED
        meeting.status = MeetingStatus.COMPLETED
        db.commit()
        logger.info(f"Successfully processed meeting {meeting_id}. Status set to COMPLETED.")

    except Exception as e:
        logger.error(f"Error processing meeting {meeting_id}: {e}", exc_info=True)
        meeting = db.query(Meeting).filter(Meeting.id == uuid.UUID(meeting_id)).first()
        if meeting:
            meeting.status = MeetingStatus.FAILED
            db.commit()
    finally:
        db.close()

    return {"status": "success", "meeting_id": meeting_id}