import time
import logging
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Meeting, MeetingStatus
import uuid
from worker import celery_app

from .transcription_service import transcribe_audio_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(name="process_meeting_file")
def process_meeting_file(meeting_id: str):
    logger.info(f"Starting processing for meeting_id: {meeting_id}")
    
    db: Session = SessionLocal()
    try:
        meeting = db.query(Meeting).filter(Meeting.id == uuid.UUID(meeting_id)).first()
        if not meeting:
            logger.error(f"Meeting with id {meeting_id} not found.")
            return

        meeting.status = MeetingStatus.PROCESSING
        db.commit()
        logger.info(f"Status updated to PROCESSING for meeting {meeting_id}")

        # === STEP 1: TRANSCRIPTION ===
        try:
            transcript_text = transcribe_audio_file(meeting.file_path)
            meeting.transcript = transcript_text
            db.commit()
            logger.info(f"Successfully transcribed meeting {meeting_id}")
        except Exception as e:
            logger.error(f"Transcription failed for meeting {meeting_id}: {e}")
            # Set status to FAILED and re-raise the exception to stop the pipeline
            meeting.status = MeetingStatus.FAILED
            db.commit()
            raise e

        # === SIMULATED AI PIPELINE - STEP 2: SUMMARIZATION (for now) ===
        logger.info("Simulating summarization...")
        time.sleep(10)
        meeting.summary = "This is a dummy summary for the real transcript."
        db.commit()
        
        meeting.status = MeetingStatus.COMPLETED
        db.commit()
        logger.info(f"Successfully processed meeting {meeting_id}. Status set to COMPLETED.")

    except Exception as e:
        logger.error(f"An error occurred in the pipeline for meeting {meeting_id}: {e}", exc_info=True)
        # The status might have already been set to FAILED, but we ensure it here.
        meeting = db.query(Meeting).filter(Meeting.id == uuid.UUID(meeting_id)).first()
        if meeting and meeting.status != MeetingStatus.FAILED:
            meeting.status = MeetingStatus.FAILED
            db.commit()
    finally:
        db.close()

    return {"status": "success", "meeting_id": meeting_id}