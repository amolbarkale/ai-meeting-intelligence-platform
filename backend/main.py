from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sqlite3
import os
from datetime import datetime
import uuid
from pathlib import Path
from transcription_service import process_transcription_async
from analysis_service import process_analysis_async
from knowledge_base_service import index_meeting_async
import json

app = FastAPI(title="Meeting Intelligence Platform")

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_PATH = "meetings.db"
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def init_db():
    """Initialize database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Meetings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration INTEGER,
            status TEXT DEFAULT 'processing',
            file_path TEXT NOT NULL
        )
    """)
    
    # Transcripts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transcripts (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        )
    """)
    
    # Summaries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            summary TEXT,
            key_points TEXT,
            action_items TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        )
    """)
    
    # Sentiment analysis table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sentiment_analysis (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            overall_sentiment TEXT,
            sentiment_scores TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        )
    """)
    
    # Topics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            topic_name TEXT,
            relevance_score REAL,
            mentions INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        )
    """)
    
    # Knowledge base table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            content TEXT,
            embedding TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        )
    """)
    
    # Highlights table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS highlights (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            highlight_text TEXT,
            timestamp INTEGER,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/upload")
async def upload_meeting(file: UploadFile = File(...)):
    """Upload a meeting audio/video file"""
    try:
        meeting_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        file_path = UPLOAD_DIR / f"{meeting_id}{file_extension}"
        
        # Save file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Store in database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO meetings (id, filename, file_path, status)
            VALUES (?, ?, ?, ?)
        """, (meeting_id, file.filename, str(file_path), "processing"))
        conn.commit()
        conn.close()
        
        process_transcription_async(str(file_path), meeting_id)
        
        return {
            "meeting_id": meeting_id,
            "filename": file.filename,
            "status": "processing",
            "message": "File uploaded successfully. Transcription in progress..."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meetings")
async def get_meetings():
    """Get all meetings"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM meetings ORDER BY upload_date DESC")
        meetings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return meetings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meetings/{meeting_id}")
async def get_meeting(meeting_id: str):
    """Get meeting details with all analyses"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get meeting
        cursor.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,))
        meeting = dict(cursor.fetchone() or {})
        
        # Get transcript
        cursor.execute("SELECT content FROM transcripts WHERE meeting_id = ?", (meeting_id,))
        transcript = cursor.fetchone()
        meeting["transcript"] = transcript[0] if transcript else None
        
        # Get summary
        cursor.execute("SELECT * FROM summaries WHERE meeting_id = ?", (meeting_id,))
        summary = cursor.fetchone()
        if summary:
            summary_dict = dict(summary)
            summary_dict["key_points"] = json.loads(summary_dict.get("key_points", "[]"))
            summary_dict["action_items"] = json.loads(summary_dict.get("action_items", "[]"))
            meeting["summary"] = summary_dict
        
        # Get sentiment
        cursor.execute("SELECT * FROM sentiment_analysis WHERE meeting_id = ?", (meeting_id,))
        sentiment = cursor.fetchone()
        if sentiment:
            sentiment_dict = dict(sentiment)
            sentiment_dict["sentiment_scores"] = json.loads(sentiment_dict.get("sentiment_scores", "{}"))
            meeting["sentiment"] = sentiment_dict
        
        # Get topics
        cursor.execute("SELECT * FROM topics WHERE meeting_id = ?", (meeting_id,))
        topics = [dict(row) for row in cursor.fetchall()]
        meeting["topics"] = topics
        
        conn.close()
        return meeting
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meetings/{meeting_id}/transcript")
async def get_transcript(meeting_id: str):
    """Get transcript for a meeting"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM transcripts WHERE meeting_id = ?", (meeting_id,))
        transcript = cursor.fetchone()
        conn.close()
        
        if not transcript:
            raise HTTPException(status_code=404, detail="Transcript not found")
        
        return dict(transcript)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meetings/{meeting_id}/status")
async def get_meeting_status(meeting_id: str):
    """Get current processing status of a meeting"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, status FROM meetings WHERE id = ?", (meeting_id,))
        meeting = cursor.fetchone()
        conn.close()
        
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        return dict(meeting)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search_knowledge_base(q: str = Query(..., min_length=1)):
    """Search across all meetings"""
    try:
        from knowledge_base_service import kb_service
        
        results = kb_service.search(q, n_results=10)
        
        # Enrich results with meeting info
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        enriched_results = []
        for result in results:
            cursor.execute("SELECT filename FROM meetings WHERE id = ?", (result["meeting_id"],))
            meeting = cursor.fetchone()
            if meeting:
                result["meeting_filename"] = meeting["filename"]
                enriched_results.append(result)
        
        conn.close()
        return {"query": q, "results": enriched_results, "count": len(enriched_results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/overview")
async def get_analytics_overview():
    """Get overview statistics"""
    try:
        from analytics_service import analytics_service
        stats = analytics_service.get_overview_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/sentiment-distribution")
async def get_sentiment_distribution():
    """Get sentiment distribution across meetings"""
    try:
        from analytics_service import analytics_service
        distribution = analytics_service.get_sentiment_distribution()
        return distribution
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/top-topics")
async def get_top_topics(limit: int = 10):
    """Get top discussed topics"""
    try:
        from analytics_service import analytics_service
        topics = analytics_service.get_top_topics(limit)
        return {"topics": topics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/sentiment-timeline")
async def get_sentiment_timeline(days: int = 30):
    """Get sentiment trend over time"""
    try:
        from analytics_service import analytics_service
        timeline = analytics_service.get_sentiment_timeline(days)
        return {"timeline": timeline}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/processing-stats")
async def get_processing_stats():
    """Get meeting processing statistics"""
    try:
        from analytics_service import analytics_service
        stats = analytics_service.get_meeting_processing_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/knowledge-graph")
async def get_knowledge_graph():
    """Get knowledge graph data"""
    try:
        from analytics_service import analytics_service
        graph_data = analytics_service.get_knowledge_graph_data()
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
