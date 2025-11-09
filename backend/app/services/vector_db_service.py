import logging
from typing import List, Dict, Any

from app.services.graph_service import search_meetings

logger = logging.getLogger(__name__)


def add_transcript_to_db(meeting_id: str, transcript: str) -> None:
    """
    Backwards-compatible no-op. All knowledge persistence lives in the Neo4j graph layer.
    """
    logger.debug(
        "add_transcript_to_db called for meeting %s. Graph persistence happens elsewhere; nothing to do.",
        meeting_id,
    )


def search_transcripts(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Delegates search to the Neo4j graph service.
    """
    if not query:
        return []
    logger.info("Routing semantic search to Neo4j graph, query='%s'", query)
    matches = search_meetings(query, limit=top_k)
    results: List[Dict[str, Any]] = []
    for match in matches:
        results.append(
            {
                "content": match.get("summary") or "",
                "metadata": {
                    "meeting_id": match.get("meeting_id"),
                    "title": match.get("title"),
                    "tags": match.get("tags"),
                    "created_at": match.get("created_at"),
                },
                "distance": 0.0,  # placeholder since we're not computing vector distance
            }
        )
    return results