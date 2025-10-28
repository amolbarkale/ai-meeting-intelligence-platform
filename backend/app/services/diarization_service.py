import logging
import torch
from pyannote.audio import Pipeline
from app.core.config import settings

logger = logging.getLogger(__name__)

# --- Initialize the Diarization Pipeline ---
# This is a heavy object, so we initialize it once when the module is loaded.
# This assumes the Celery worker will load this module.
diarization_pipeline = None

if hasattr(settings, 'HF_TOKEN') and settings.HF_TOKEN and settings.HF_TOKEN.strip():
    try:
        logger.info("Initializing Pyannote speaker diarization pipeline...")
        diarization_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=settings.HF_TOKEN
        )
        # If you have a GPU, you can move it to the GPU
        # diarization_pipeline.to(torch.device("cuda"))
        logger.info("Pyannote pipeline initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Pyannote pipeline: {e}", exc_info=True)
        diarization_pipeline = None
else:
    logger.warning("HF_TOKEN not set - diarization will be skipped, speakers will be marked as UNKNOWN_SPEAKER")

def perform_diarization(audio_file_path: str):
    """
    Performs speaker diarization on an audio file.
    If HF_TOKEN is not available, returns None to indicate no diarization.

    Args:
        audio_file_path: Path to the audio file (WAV format recommended).

    Returns:
        The diarization result object from Pyannote, or None if diarization is not available.
    """
    if diarization_pipeline is None:
        logger.warning("Diarization pipeline not available - skipping diarization")
        return None
        
    logger.info(f"Performing speaker diarization on {audio_file_path}...")
    try:
        diarization_result = diarization_pipeline(audio_file_path)
        logger.info("Diarization completed.")
        return diarization_result
    except Exception as e:
        logger.error(f"Error during diarization: {e}", exc_info=True)
        raise e