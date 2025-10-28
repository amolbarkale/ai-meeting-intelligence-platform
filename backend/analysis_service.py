import requests
import json
import sqlite3
import uuid
import re
from typing import Dict, List, Optional
import threading
from knowledge_base_service import index_meeting_async

class AnalysisService:
    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        self.ollama_base_url = ollama_base_url
        self.model = "mistral"  # Using Mistral as it's lightweight and effective
        
    def analyze_meeting(self, meeting_id: str, transcript: str) -> bool:
        """
        Run all analyses on a transcript
        Returns True if successful
        """
        try:
            # Generate summary and key points
            summary_result = self._generate_summary(transcript)
            if summary_result:
                self._save_summary(meeting_id, summary_result)
            
            # Analyze sentiment
            sentiment_result = self._analyze_sentiment(transcript)
            if sentiment_result:
                self._save_sentiment(meeting_id, sentiment_result)
            
            # Extract topics
            topics_result = self._extract_topics(transcript)
            if topics_result:
                self._save_topics(meeting_id, topics_result)
            
            # Index to knowledge base
            summary_text = summary_result.get("summary", "") if summary_result else ""
            index_meeting_async(meeting_id, transcript, summary_text)
            
            # Update status
            self._update_meeting_status(meeting_id, "completed")
            return True
            
        except Exception as e:
            print(f"Analysis error: {str(e)}")
            self._update_meeting_status(meeting_id, "error")
            return False
    
    def _generate_summary(self, transcript: str) -> Optional[Dict]:
        """Generate summary, key points, and action items"""
        try:
            prompt = f"""Analyze this meeting transcript and provide:
1. A concise summary (2-3 sentences)
2. Key points (3-5 bullet points)
3. Action items (2-4 bullet points with owner if mentioned)

Transcript:
{transcript[:2000]}

Respond in JSON format:
{{
    "summary": "...",
    "key_points": ["point1", "point2", ...],
    "action_items": ["action1", "action2", ...]
}}"""
            
            response = self._call_ollama(prompt)
            if response:
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            return None
        except Exception as e:
            print(f"Summary generation error: {str(e)}")
            return None
    
    def _analyze_sentiment(self, transcript: str) -> Optional[Dict]:
        """Analyze overall sentiment and sentiment distribution"""
        try:
            prompt = f"""Analyze the sentiment of this meeting transcript.
Provide:
1. Overall sentiment (positive, neutral, or negative)
2. Sentiment score (0-100, where 0 is very negative and 100 is very positive)
3. Brief explanation

Transcript:
{transcript[:2000]}

Respond in JSON format:
{{
    "overall_sentiment": "positive/neutral/negative",
    "sentiment_score": 75,
    "explanation": "..."
}}"""
            
            response = self._call_ollama(prompt)
            if response:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            return None
        except Exception as e:
            print(f"Sentiment analysis error: {str(e)}")
            return None
    
    def _extract_topics(self, transcript: str) -> Optional[List[Dict]]:
        """Extract main topics discussed in the meeting"""
        try:
            prompt = f"""Extract the main topics discussed in this meeting transcript.
For each topic, provide:
1. Topic name
2. Relevance score (0-100)
3. Number of mentions

Provide top 5 topics.

Transcript:
{transcript[:2000]}

Respond in JSON format:
{{
    "topics": [
        {{"name": "topic1", "relevance_score": 85, "mentions": 5}},
        {{"name": "topic2", "relevance_score": 70, "mentions": 3}}
    ]
}}"""
            
            response = self._call_ollama(prompt)
            if response:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    return data.get("topics", [])
            return None
        except Exception as e:
            print(f"Topic extraction error: {str(e)}")
            return None
    
    def _call_ollama(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Call Ollama API with retry logic"""
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": 0.7,
                    },
                    timeout=120
                )
                
                if response.status_code == 200:
                    return response.json().get("response", "")
                else:
                    print(f"Ollama API error: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print(f"Connection error (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)
            except Exception as e:
                print(f"Ollama call error: {str(e)}")
        
        return None
    
    def _save_summary(self, meeting_id: str, summary_data: Dict):
        """Save summary to database"""
        conn = sqlite3.connect("meetings.db")
        cursor = conn.cursor()
        summary_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO summaries (id, meeting_id, summary, key_points, action_items)
            VALUES (?, ?, ?, ?, ?)
        """, (
            summary_id,
            meeting_id,
            summary_data.get("summary", ""),
            json.dumps(summary_data.get("key_points", [])),
            json.dumps(summary_data.get("action_items", []))
        ))
        
        conn.commit()
        conn.close()
    
    def _save_sentiment(self, meeting_id: str, sentiment_data: Dict):
        """Save sentiment analysis to database"""
        conn = sqlite3.connect("meetings.db")
        cursor = conn.cursor()
        sentiment_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO sentiment_analysis (id, meeting_id, overall_sentiment, sentiment_scores)
            VALUES (?, ?, ?, ?)
        """, (
            sentiment_id,
            meeting_id,
            sentiment_data.get("overall_sentiment", "neutral"),
            json.dumps(sentiment_data)
        ))
        
        conn.commit()
        conn.close()
    
    def _save_topics(self, meeting_id: str, topics: List[Dict]):
        """Save extracted topics to database"""
        conn = sqlite3.connect("meetings.db")
        cursor = conn.cursor()
        
        for topic in topics:
            topic_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO topics (id, meeting_id, topic_name, relevance_score, mentions)
                VALUES (?, ?, ?, ?, ?)
            """, (
                topic_id,
                meeting_id,
                topic.get("name", ""),
                topic.get("relevance_score", 0),
                topic.get("mentions", 0)
            ))
        
        conn.commit()
        conn.close()
    
    def _update_meeting_status(self, meeting_id: str, status: str):
        """Update meeting status in database"""
        conn = sqlite3.connect("meetings.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE meetings SET status = ? WHERE id = ?
        """, (status, meeting_id))
        conn.commit()
        conn.close()

# Global analysis service instance
analysis_service = AnalysisService()

def process_analysis_async(meeting_id: str, transcript: str):
    """Process analysis in background thread"""
    thread = threading.Thread(
        target=analysis_service.analyze_meeting,
        args=(meeting_id, transcript),
        daemon=True
    )
    thread.start()
