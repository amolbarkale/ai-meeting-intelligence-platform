import os
import uuid
import time
import logging
import pandas as pd
import ffmpeg
from tempfile import NamedTemporaryFile
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Meeting, MeetingStatus
from worker import celery_app

from .diarization_service import perform_diarization
from .transcription_service import transcribe_audio_file
from .llm_service import generate_meeting_insights
from .vector_db_service import add_transcript_to_db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def merge_transcription_and_diarization(transcription_df: pd.DataFrame, diarization) -> str:
    """
    Merges Whisper's transcription DataFrame with Pyannote's diarization results.
    If diarization is None, all speakers are marked as UNKNOWN_SPEAKER.
    """
    final_transcript = ""
    for index, row in transcription_df.iterrows():
        # Find which speaker spoke during the middle of the segment
        segment_mid_point = row['start'] + (row['end'] - row['start']) / 2
        try:
            if diarization is not None:
                # Get the speaker label for the segment's midpoint
                speaker = diarization.crop(segment_mid_point).any_label()
            else:
                speaker = "UNKNOWN_SPEAKER"
        except StopIteration:
            # If no speaker is active at the midpoint, label as unknown
            speaker = "UNKNOWN_SPEAKER"
        
        # Format the timestamp for readability (e.g., [00:05])
        start_time = f"{int(row['start'] // 60):02d}:{int(row['start'] % 60):02d}"
        
        final_transcript += f"[{start_time}] {speaker}: {row['text'].strip()}\n"
    
    return final_transcript


@celery_app.task(name="process_meeting_file", bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def process_meeting_file(self, meeting_id: str):
    """
    The main Celery task that orchestrates the entire AI pipeline:
    1. Preprocesses the audio file.
    2. Performs speaker diarization.
    3. Transcribes the audio.
    4. Merges the results.
    5. Generates AI insights from the final transcript.
    """
    logger.info(f"Starting AI pipeline for meeting_id: {meeting_id}")
    
    db: Session = SessionLocal()
    meeting = db.query(Meeting).filter(Meeting.id == uuid.UUID(meeting_id)).first()
    if not meeting:
        logger.error(f"Meeting with id {meeting_id} not found in database.")
        db.close()
        return

    # Use a temporary file for the standardized WAV audio
    temp_wav_path = None
    try:
        meeting.status = MeetingStatus.PROCESSING
        db.commit()
        logger.info(f"Status updated to PROCESSING for meeting {meeting_id}")

        # --- Step 0: Pre-process Audio to a standard format ---
        with NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav_file:
            temp_wav_path = temp_wav_file.name
        
        logger.info(f"Converting {meeting.file_path} to standardized WAV at {temp_wav_path}")
        (
            ffmpeg
            .input(meeting.file_path)
            .output(temp_wav_path, ar=16000, ac=1, acodec='pcm_s16le') # 16kHz, mono, 16-bit PCM WAV
            .run(cmd='ffmpeg', capture_stdout=True, capture_stderr=True, overwrite_output=True)
        )

        # --- Step 1: Diarization (Who spoke when?) ---
        diarization_result = perform_diarization(temp_wav_path)

        # --- Step 2: Transcription (What was said?) ---
        # Note: We pass the standardized temp_wav_path now
        transcription_df = transcribe_audio_file(temp_wav_path) 

        # --- Step 3: Merge Results ---
        logger.info("Merging transcription and diarization results...")
        speaker_labeled_transcript = merge_transcription_and_diarization(transcription_df, diarization_result)
        meeting.transcript = speaker_labeled_transcript
        db.commit()
        logger.info(f"Successfully created speaker-labeled transcript for meeting {meeting_id}")

        # --- Step 4: Generate AI Insights ---
        insights = generate_meeting_insights(meeting.transcript)
        
        meeting.summary = insights.get('abstract_summary')
        meeting.key_points = insights.get('key_points')
        meeting.action_items = insights.get('action_items')
        meeting.sentiment = insights.get('sentiment_analysis')
        meeting.tags = insights.get('tags')
        meeting.knowledge_graph = insights.get('knowledge_graph')

        db.commit()
        logger.info(f"Successfully generated AI insights for meeting {meeting_id}")

        # --- Step 5: Add to Knowledge Base ---
        add_transcript_to_db(str(meeting.id), meeting.transcript)

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
        if temp_wav_path and os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
            logger.info(f"Cleaned up temporary file: {temp_wav_path}")
        
        db.close()

    return {"status": "success", "meeting_id": meeting_id}