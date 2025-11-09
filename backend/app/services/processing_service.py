import os
import uuid
import logging
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Meeting, MeetingStatus
from app.core.celery_app import celery_app

from .transcription_service import transcribe_audio_file, merge_transcription_and_diarization
from .llm_service import generate_meeting_insights
from .vector_db_service import add_transcript_to_db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(
    name="process_meeting_file",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def process_meeting_file(self, meeting_id: str):
    """
    The main Celery task that orchestrates the entire AI pipeline:
    1. Transcribes audio with Deepgram API (includes diarization)
    2. Formats transcript with speaker labels
    3. Generates AI insights from the final transcript
    4. (Placeholder) Stores results in future knowledge base
    """
    logger.info(f"Starting AI pipeline for meeting_id: {meeting_id}")

    db: Session = SessionLocal()
    meeting = db.query(Meeting).filter(Meeting.id == uuid.UUID(meeting_id)).first()
    if not meeting:
        logger.error(f"Meeting with id {meeting_id} not found in database.")
        db.close()
        return

    original_file_path = meeting.file_path

    try:
        meeting.status = MeetingStatus.PROCESSING
        db.commit()
        logger.info(f"Status updated to PROCESSING for meeting {meeting_id}")

        # --- Step 1: Transcribe with Deepgram (includes diarization) ---
        logger.info(f"Starting Deepgram transcription with diarization for {meeting.file_path}")
        transcription_df = transcribe_audio_file(meeting.file_path)

        # --- Step 2: Merge transcription and diarization (Deepgram provides both) ---
        logger.info("Merging transcription and diarization results...")
        speaker_labeled_transcript = merge_transcription_and_diarization(transcription_df)
        meeting.transcript = speaker_labeled_transcript
        db.commit()
        logger.info(f"Successfully created speaker-labeled transcript for meeting {meeting_id}")

        # --- Step 3: Generate AI Insights ---
        logger.info("Generating AI insights...")
        insights = generate_meeting_insights(meeting.transcript)

        meeting.summary = insights.get("abstract_summary")
        meeting.key_points = insights.get("key_points")
        meeting.action_items = insights.get("action_items")
        meeting.sentiment = insights.get("sentiment_analysis")
        meeting.tags = insights.get("tags")
        meeting.knowledge_graph = insights.get("knowledge_graph")

        db.commit()
        logger.info(f"Successfully generated AI insights for meeting {meeting_id}")

        # --- Step 4: Add to Knowledge Base ---
        # TODO: Replace ChromaDB with graph DB
        # add_transcript_to_db(str(meeting.id), meeting.transcript)
        logger.info("Skipping vector DB storage - will be replaced with graph DB")

        # --- Final Step: Mark as COMPLETED ---
        meeting.status = MeetingStatus.COMPLETED
        db.commit()
        logger.info(f"Pipeline finished successfully for meeting {meeting_id}.")

    except Exception as e:
        logger.error(f"An error occurred in the pipeline for meeting {meeting_id}: {e}", exc_info=True)
        if meeting:
            meeting.status = MeetingStatus.FAILED
            db.commit()

    finally:
        try:
            if (
                meeting
                and meeting.status == MeetingStatus.COMPLETED
                and original_file_path
                and os.path.exists(original_file_path)
            ):
                os.remove(original_file_path)
                logger.info(f"Removed temporary file at {original_file_path} after successful processing.")
        except Exception as cleanup_error:
            logger.warning(f"Failed to remove temporary file at {original_file_path}: {cleanup_error}")
        finally:
            db.close()

    return {"status": "success", "meeting_id": meeting_id}
