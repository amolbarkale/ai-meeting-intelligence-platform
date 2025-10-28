import sqlite3
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

class AnalyticsService:
    def __init__(self):
        self.db_path = "meetings.db"
    
    def get_overview_stats(self) -> Dict:
        """Get overall platform statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total meetings
        cursor.execute("SELECT COUNT(*) FROM meetings")
        total_meetings = cursor.fetchone()[0]
        
        # Completed meetings
        cursor.execute("SELECT COUNT(*) FROM meetings WHERE status = 'completed'")
        completed_meetings = cursor.fetchone()[0]
        
        # Processing meetings
        cursor.execute("SELECT COUNT(*) FROM meetings WHERE status IN ('processing', 'transcribed')")
        processing_meetings = cursor.fetchone()[0]
        
        # Error meetings
        cursor.execute("SELECT COUNT(*) FROM meetings WHERE status = 'error'")
        error_meetings = cursor.fetchone()[0]
        
        # Average sentiment
        cursor.execute("""
            SELECT AVG(CAST(json_extract(sentiment_scores, '$.sentiment_score') AS FLOAT))
            FROM sentiment_analysis
        """)
        avg_sentiment = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_meetings": total_meetings,
            "completed_meetings": completed_meetings,
            "processing_meetings": processing_meetings,
            "error_meetings": error_meetings,
            "completion_rate": round((completed_meetings / total_meetings * 100) if total_meetings > 0 else 0, 1),
            "average_sentiment_score": round(avg_sentiment, 1)
        }
    
    def get_sentiment_distribution(self) -> Dict:
        """Get distribution of sentiment across meetings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT overall_sentiment, COUNT(*) as count
            FROM sentiment_analysis
            GROUP BY overall_sentiment
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        distribution = {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }
        
        for sentiment, count in results:
            if sentiment.lower() in distribution:
                distribution[sentiment.lower()] = count
        
        return distribution
    
    def get_top_topics(self, limit: int = 10) -> List[Dict]:
        """Get most frequently discussed topics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT topic_name, COUNT(*) as frequency, AVG(relevance_score) as avg_relevance
            FROM topics
            GROUP BY topic_name
            ORDER BY frequency DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "name": row[0],
                "frequency": row[1],
                "avg_relevance": round(row[2], 1)
            }
            for row in results
        ]
    
    def get_sentiment_timeline(self, days: int = 30) -> List[Dict]:
        """Get sentiment trend over time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT 
                DATE(m.upload_date) as date,
                AVG(CAST(json_extract(s.sentiment_scores, '$.sentiment_score') AS FLOAT)) as avg_sentiment,
                COUNT(*) as meeting_count
            FROM meetings m
            LEFT JOIN sentiment_analysis s ON m.id = s.meeting_id
            WHERE m.upload_date >= ?
            GROUP BY DATE(m.upload_date)
            ORDER BY date ASC
        """, (cutoff_date.isoformat(),))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "date": row[0],
                "sentiment_score": round(row[1], 1) if row[1] else 0,
                "meeting_count": row[2]
            }
            for row in results
        ]
    
    def get_meeting_processing_stats(self) -> Dict:
        """Get statistics about meeting processing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Meetings with transcripts
        cursor.execute("SELECT COUNT(*) FROM transcripts")
        transcribed = cursor.fetchone()[0]
        
        # Meetings with summaries
        cursor.execute("SELECT COUNT(*) FROM summaries")
        summarized = cursor.fetchone()[0]
        
        # Meetings with sentiment analysis
        cursor.execute("SELECT COUNT(*) FROM sentiment_analysis")
        sentiment_analyzed = cursor.fetchone()[0]
        
        # Meetings with topics
        cursor.execute("SELECT COUNT(*) FROM topics")
        topics_extracted = cursor.fetchone()[0]
        
        # Total meetings
        cursor.execute("SELECT COUNT(*) FROM meetings")
        total = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "transcribed": transcribed,
            "summarized": summarized,
            "sentiment_analyzed": sentiment_analyzed,
            "topics_extracted": topics_extracted,
            "total_meetings": total,
            "transcription_rate": round((transcribed / total * 100) if total > 0 else 0, 1),
            "analysis_rate": round((summarized / total * 100) if total > 0 else 0, 1)
        }
    
    def get_knowledge_graph_data(self) -> Dict:
        """Get data for knowledge graph visualization"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get top topics as nodes
        cursor.execute("""
            SELECT topic_name, COUNT(*) as frequency
            FROM topics
            GROUP BY topic_name
            ORDER BY frequency DESC
            LIMIT 15
        """)
        
        topics = cursor.fetchall()
        
        # Get topic co-occurrences (topics in same meeting)
        cursor.execute("""
            SELECT t1.topic_name, t2.topic_name, COUNT(*) as co_occurrence
            FROM topics t1
            JOIN topics t2 ON t1.meeting_id = t2.meeting_id AND t1.topic_name < t2.topic_name
            GROUP BY t1.topic_name, t2.topic_name
            HAVING co_occurrence > 0
            ORDER BY co_occurrence DESC
            LIMIT 20
        """)
        
        edges = cursor.fetchall()
        conn.close()
        
        # Build nodes
        nodes = [
            {
                "id": topic[0],
                "label": topic[0],
                "size": min(topic[1] * 10, 100),
                "frequency": topic[1]
            }
            for topic in topics
        ]
        
        # Build edges
        edge_list = [
            {
                "source": edge[0],
                "target": edge[1],
                "weight": edge[2]
            }
            for edge in edges
        ]
        
        return {
            "nodes": nodes,
            "edges": edge_list
        }

# Global analytics service instance
analytics_service = AnalyticsService()
