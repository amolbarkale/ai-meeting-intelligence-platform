from fastapi import APIRouter, Query
from app.api.v1 import schemas
from app.services.vector_db_service import search_transcripts

router = APIRouter()

@router.get("", response_model=schemas.SearchResponse)
def search_in_meetings(
    query: str = Query(..., min_length=3, description="The search query to find relevant meeting snippets."),
    top_k: int = Query(5, ge=1, le=20, description="Number of results to return (1-20)")
):
    """
    Search across all processed meetings for a specific query.
    """
    results = search_transcripts(query, top_k=top_k)
    return schemas.SearchResponse(query=query, results=results)