import os
import subprocess
import ffmpeg
import logging
from tempfile import NamedTemporaryFile
from app.core.config import settings

logger = logging.getLogger(__name__)

def transcribe_audio_file(input_file_path: str) -> str:
    """
    Transcribes an audio/video file using whisper.cpp.

    Args:
        input_file_path: The path to the audio or video file.

    Returns:
        The transcribed text.
    
    Raises:
        Exception: If ffmpeg preprocessing or whisper.cpp transcription fails.
    """
    logger.info(f"Starting transcription for {input_file_path}")

    # --- Pre-processing with ffmpeg ---
    # Use a temporary file for the WAV output
    with NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav_file:
        temp_wav_path = temp_wav_file.name

    try:
        logger.info(f"Preprocessing audio to 16kHz mono WAV: {temp_wav_path}")
        # Use ffmpeg-python to convert the input file to the format Whisper needs
        (
            ffmpeg
            .input(input_file_path)
            .output(temp_wav_path, ar=16000, ac=1, acodec='pcm_s16le')
            .run(cmd='ffmpeg', capture_stdout=True, capture_stderr=True, overwrite_output=True)
        )
    except ffmpeg.Error as e:
        logger.error(f"FFmpeg error: {e.stderr.decode()}")
        os.remove(temp_wav_path)
        raise Exception(f"FFmpeg failed to process the audio file. Error: {e.stderr.decode()}")

    # --- Transcription with whisper.cpp (from Solution 2) ---
    try:
        logger.info("Running whisper.cpp transcription...")
        command = [
            settings.WHISPER_CPP_PATH,
            "-m", settings.WHISPER_CPP_MODEL_PATH,
            "-f", temp_wav_path,
            "-otxt", # Output as plain text
            "-nt" # No timestamps
        ]
        
        # The result will be printed to stdout
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        transcript = result.stdout.strip()
        
        logger.info("Transcription completed successfully.")
        return transcript

    except subprocess.CalledProcessError as e:
        logger.error(f"whisper.cpp failed with exit code {e.returncode}")
        logger.error(f"whisper.cpp stderr: {e.stderr}")
        raise Exception(f"Transcription with whisper.cpp failed. Error: {e.stderr}")

    finally:
        # --- Cleanup ---
        logger.info(f"Cleaning up temporary WAV file: {temp_wav_path}")
        os.remove(temp_wav_path)