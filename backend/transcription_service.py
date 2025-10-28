import subprocess
import os
from pathlib import Path
import sqlite3
import json
import uuid
from datetime import datetime
import threading
from typing import Optional
from analysis_service import process_analysis_async

class TranscriptionService:
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.whisper_cmd = "whisper"  # Assumes whisper is installed via pip
        
    def transcribe_audio(self, file_path: str, meeting_id: str) -> bool:
        """
        Transcribe audio file using Whisper and save to database
        Returns True if successful, False otherwise
        """
        try:
            wav_path = self._convert_to_wav(file_path)
            
            # Run Whisper transcription
            output_dir = Path("transcripts")
            output_dir.mkdir(exist_ok=True)
            
            result = subprocess.run(
                [
                    self.whisper_cmd,
                    wav_path,
                    "--model", self.model_size,
                    "--output_format", "json",
                    "--output_dir", str(output_dir),
                    "--device", "cpu"  # Change to "cuda" if GPU available
                ],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode != 0:
                print(f"Whisper error: {result.stderr}")
                self._update_meeting_status(meeting_id, "error")
                return False
            
            # Read transcription result
            json_file = output_dir / f"{Path(wav_path).stem}.json"
            if json_file.exists():
                with open(json_file, "r") as f:
                    transcript_data = json.load(f)
                
                transcript_text = transcript_data.get("text", "")
                
                # Save to database
                self._save_transcript(meeting_id, transcript_text)
                self._update_meeting_status(meeting_id, "transcribed")
                
                # Cleanup
                json_file.unlink()
                if wav_path != file_path:
                    Path(wav_path).unlink()
                
                return True
            
            return False
            
        except subprocess.TimeoutExpired:
            print(f"Transcription timeout for {meeting_id}")
            self._update_meeting_status(meeting_id, "error")
            return False
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            self._update_meeting_status(meeting_id, "error")
            return False
    
    def _convert_to_wav(self, file_path: str) -> str:
        """Convert audio file to WAV format using ffmpeg"""
        try:
            output_path = f"{Path(file_path).stem}_converted.wav"
            subprocess.run(
                ["ffmpeg", "-i", file_path, "-acodec", "pcm_s16le", "-ar", "16000", output_path, "-y"],
                capture_output=True,
                timeout=300
            )
            return output_path if Path(output_path).exists() else file_path
        except Exception as e:
            print(f"Audio conversion error: {str(e)}")
            return file_path
    
    def _save_transcript(self, meeting_id: str, transcript_text: str):
        """Save transcript to database"""
        conn = sqlite3.connect("meetings.db")
        cursor = conn.cursor()
        transcript_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO transcripts (id, meeting_id, content)
            VALUES (?, ?, ?)
        """, (transcript_id, meeting_id, transcript_text))
        
        conn.commit()
        conn.close()
        
        process_analysis_async(meeting_id, transcript_text)
    
    def _update_meeting_status(self, meeting_id: str, status: str):
        """Update meeting status in database"""
        conn = sqlite3.connect("meetings.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE meetings SET status = ? WHERE id = ?
        """, (status, meeting_id))
        conn.commit()
        conn.close()

# Global transcription service instance
transcription_service = TranscriptionService(model_size="base")

def process_transcription_async(file_path: str, meeting_id: str):
    """Process transcription in background thread"""
    thread = threading.Thread(
        target=transcription_service.transcribe_audio,
        args=(file_path, meeting_id),
        daemon=True
    )
    thread.start()
