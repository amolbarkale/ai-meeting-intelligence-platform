import logging
from typing import List, Dict, Optional
import threading

from app.services import graph_service

logger = logging.getLogger(__name__)


def index_meeting(meeting_id: str, transcript: str, summary: str, **metadata: Optional[str]) -> bool:
    """
    Persist minimal meeting signals into the Neo4j knowledge graph.

    Backwards compatible replacement for the legacy ChromaDB implementation.
    """
    payload: Dict[str, Optional[str]] = {
        "id": meeting_id,
        "transcript": transcript or "",
        "summary": summary or "",
        "key_points": metadata.get("key_points") if metadata else "",
        "action_items": metadata.get("action_items") if metadata else "",
        "sentiment": metadata.get("sentiment") if metadata else "",
        "tags": metadata.get("tags") if metadata else "",
        "original_filename": metadata.get("original_filename") if metadata else "",
        "saved_filename": metadata.get("saved_filename") if metadata else "",
        "knowledge_graph": metadata.get("knowledge_graph") if metadata else "",
        "created_at": metadata.get("created_at") if metadata else None,
        "updated_at": metadata.get("updated_at") if metadata else None,
        "status": metadata.get("status") if metadata else None,
    }

    try:
        graph_service.upsert_meeting_graph(payload)
        logger.info("Indexed meeting %s into Neo4j knowledge base", meeting_id)
        return True
    except Exception as exc:
        logger.error("Knowledge base indexing error for meeting %s: %s", meeting_id, exc)
        return False


def search(query: str, n_results: int = 5) -> List[Dict[str, str]]:
    """
    Search across meeting summaries/tags/transcripts via the Neo4j graph service.
    """
    if not query:
        return []
    try:
        results = graph_service.search_meetings(query, limit=n_results)
        return results
    except Exception as exc:
        logger.error("Knowledge base search error for query '%s': %s", query, exc)
        return []


def fetch_context(meeting_id: str) -> Optional[Dict[str, str]]:
    """
    Fetch rich meeting context used for RAG/chat experiences.
    """
    try:
        return graph_service.fetch_meeting_context(meeting_id)
    except Exception as exc:
        logger.error("Failed to fetch meeting context for %s: %s", meeting_id, exc)
        return None


def index_meeting_async(meeting_id: str, transcript: str, summary: str, **metadata: Optional[str]):
    """
    Backwards compatible asynchronous indexer.
    """

    thread = threading.Thread(
        target=index_meeting,
        args=(meeting_id, transcript, summary),
        kwargs=metadata,
        daemon=True,
    )
    thread.start()
