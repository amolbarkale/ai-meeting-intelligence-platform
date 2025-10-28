from fastapi import APIRouter, Query
from app.api.v1 import schemas
from app.services.vector_db_service import search_transcripts

router = APIRouter()

@router.get("", response_model=schemas.SearchResponse)
def search_in_meetings(
    query: str = Query(..., min_length=3, description="The search query to find relevant meeting snippets.")
):
    """
    Search across all processed meetings for a specific query.
    """
    results = search_transcripts(query)
    return schemas.SearchResponse(query=query, results=results)