import chromadb
from chromadb.config import Settings
import sqlite3
import uuid
import json
from typing import List, Dict, Optional
import threading

class KnowledgeBaseService:
    def __init__(self, persist_dir: str = "./chroma_db"):
        # Initialize ChromaDB with persistence
        settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_dir,
            anonymized_telemetry=False,
        )
        self.client = chromadb.Client(settings)
        self.collection = self.client.get_or_create_collection(
            name="meetings",
            metadata={"hnsw:space": "cosine"}
        )
    
    def index_meeting(self, meeting_id: str, transcript: str, summary: str) -> bool:
        """
        Index a meeting's content into the knowledge base
        """
        try:
            # Split transcript into chunks for better search
            chunks = self._chunk_text(transcript, chunk_size=500, overlap=100)
            
            documents = []
            metadatas = []
            ids = []
            
            for idx, chunk in enumerate(chunks):
                doc_id = f"{meeting_id}_chunk_{idx}"
                documents.append(chunk)
                metadatas.append({
                    "meeting_id": meeting_id,
                    "chunk_index": idx,
                    "type": "transcript"
                })
                ids.append(doc_id)
            
            # Add summary as a document
            summary_id = f"{meeting_id}_summary"
            documents.append(summary)
            metadatas.append({
                "meeting_id": meeting_id,
                "type": "summary"
            })
            ids.append(summary_id)
            
            # Add to ChromaDB collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            # Save to database
            self._save_knowledge_base_entries(meeting_id, documents, metadatas)
            
            return True
        except Exception as e:
            print(f"Knowledge base indexing error: {str(e)}")
            return False
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search the knowledge base for relevant content
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if not results or not results["documents"] or len(results["documents"]) == 0:
                return []
            
            # Format results
            formatted_results = []
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i] if results["distances"] else 0
                
                # Convert distance to similarity score (0-100)
                similarity_score = max(0, (1 - distance) * 100)
                
                formatted_results.append({
                    "content": doc,
                    "meeting_id": metadata.get("meeting_id"),
                    "type": metadata.get("type", "transcript"),
                    "similarity_score": round(similarity_score, 2)
                })
            
            return formatted_results
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def _save_knowledge_base_entries(self, meeting_id: str, documents: List[str], metadatas: List[Dict]):
        """Save knowledge base entries to database"""
        conn = sqlite3.connect("meetings.db")
        cursor = conn.cursor()
        
        for doc, metadata in zip(documents, metadatas):
            kb_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO knowledge_base (id, meeting_id, content)
                VALUES (?, ?, ?)
            """, (kb_id, meeting_id, doc))
        
        conn.commit()
        conn.close()

# Global knowledge base service instance
kb_service = KnowledgeBaseService()

def index_meeting_async(meeting_id: str, transcript: str, summary: str):
    """Index meeting in background thread"""
    thread = threading.Thread(
        target=kb_service.index_meeting,
        args=(meeting_id, transcript, summary),
        daemon=True
    )
    thread.start()
