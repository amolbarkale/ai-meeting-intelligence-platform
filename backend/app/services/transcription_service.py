import os
import logging
import requests
from typing import List, Dict
import pandas as pd
from app.core.config import settings

logger = logging.getLogger(__name__)

def transcribe_audio_file(input_file_path: str) -> pd.DataFrame:
    """
    Transcribes an audio/video file using Deepgram API with speaker diarization.
    
    Args:
        input_file_path: The path to the audio or video file.
    
    Returns:
        DataFrame with columns: start, end, word, speaker, confidence
    """
    logger.info(f"Starting Deepgram transcription with diarization for {input_file_path}")
    
    if not hasattr(settings, 'DEEPGRAM_API_KEY') or not settings.DEEPGRAM_API_KEY:
        raise Exception("DEEPGRAM_API_KEY is not set in environment variables")
    
    url = "https://api.deepgram.com/v1/listen?diarize=true&punctuate=true&utterances=true"
    
    headers = {
        'Authorization': f'Token {settings.DEEPGRAM_API_KEY}',
    }
    
    try:
        with open(input_file_path, 'rb') as audio_file:
            audio_data = audio_file.read()
            content_type = _get_content_type(input_file_path)
            if content_type:
                headers['Content-Type'] = content_type
            else:
                headers['Content-Type'] = 'application/octet-stream'
            
            logger.info("Sending audio to Deepgram API...")
            response = requests.post(url, headers=headers, data=audio_data, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            logger.info("Deepgram API response received successfully")
            
            return _parse_deepgram_response(result)
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Deepgram API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        raise Exception(f"Deepgram API request failed: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing Deepgram response: {e}", exc_info=True)
        raise Exception(f"Failed to process Deepgram transcription: {str(e)}")

def _get_content_type(file_path: str) -> str:
    """Determine content type from file extension"""
    ext = os.path.splitext(file_path)[1].lower()
    content_types = {
        '.wav': 'audio/wav',
        '.mp3': 'audio/mp3',
        '.m4a': 'audio/m4a',
        '.mp4': 'video/mp4',
        '.webm': 'video/webm',
    }
    return content_types.get(ext, None)

def _parse_deepgram_response(response: Dict) -> pd.DataFrame:
    """
    Parse Deepgram API response into a pandas DataFrame.
    
    Returns DataFrame with: start, end, word, speaker, confidence
    """
    words_data = []
    
    try:
        if 'results' not in response or 'channels' not in response['results']:
            raise Exception("Invalid Deepgram API response format")
        
        for channel in response['results']['channels']:
            if 'alternatives' not in channel or len(channel['alternatives']) == 0:
                continue
            
            alternative = channel['alternatives'][0]
            if 'words' not in alternative:
                continue
            
            for word_info in alternative['words']:
                words_data.append({
                    'start': word_info.get('start', 0),
                    'end': word_info.get('end', 0),
                    'word': word_info.get('word', ''),
                    'speaker': word_info.get('speaker', 0),
                    'confidence': word_info.get('confidence', 0)
                })
        
        if not words_data:
            raise Exception("No words found in Deepgram response")
        
        df = pd.DataFrame(words_data)
        logger.info(f"Parsed {len(df)} words from Deepgram response")
        return df
        
    except Exception as e:
        logger.error(f"Error parsing Deepgram response: {e}")
        logger.error(f"Response structure: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        raise Exception(f"Failed to parse Deepgram response: {str(e)}")

def merge_transcription_and_diarization(transcription_df: pd.DataFrame, diarization=None) -> str:
    """
    Merges Deepgram transcription DataFrame (which includes diarization) into formatted transcript.
    The diarization parameter is kept for compatibility but ignored since Deepgram provides speaker labels.
    
    Args:
        transcription_df: DataFrame with columns: start, end, word, speaker, confidence
        diarization: Not used (kept for compatibility), Deepgram provides speaker info in transcription_df
    
    Returns:
        Formatted transcript string with timestamps and speaker labels
    """
    if transcription_df.empty:
        return ""
    
    transcript = ""
    current_speaker = None
    current_words = []
    current_start = None
    
    for _, row in transcription_df.iterrows():
        speaker = int(row['speaker']) if pd.notna(row['speaker']) else 0
        word = str(row['word']).strip()
        
        if not word:
            continue
        
        start_time = float(row['start'])
        
        if speaker != current_speaker:
            if current_speaker is not None and current_words:
                start_min = int(current_start // 60)
                start_sec = int(current_start % 60)
                text = ' '.join(current_words)
                transcript += f"[{start_min:02d}:{start_sec:02d}] SPEAKER_{current_speaker}: {text}\n"
            
            current_speaker = speaker
            current_words = [word]
            current_start = start_time
        else:
            current_words.append(word)
    
    if current_speaker is not None and current_words:
        start_min = int(current_start // 60)
        start_sec = int(current_start % 60)
        text = ' '.join(current_words)
        transcript += f"[{start_min:02d}:{start_sec:02d}] SPEAKER_{current_speaker}: {text}\n"
    
    return transcript
