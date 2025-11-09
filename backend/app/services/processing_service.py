import os
import uuid
import logging
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Meeting, MeetingStatus
from app.core.celery_app import celery_app

from .transcription_service import transcribe_audio_file, merge_transcription_and_diarization
from .llm_service import generate_meeting_insights
from .graph_service import upsert_meeting_graph


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
    4. Stores structured insights in the Neo4j knowledge graph
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

        # --- Step 4: Persist to knowledge graph ---
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
            logger.info("Synced meeting %s to Neo4j graph", meeting_id)
        except Exception as graph_exc:
            logger.error(
                "Failed to persist meeting %s to Neo4j graph: %s",
                meeting_id,
                graph_exc,
            )

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
