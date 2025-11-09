import logging
from typing import List, Dict, Any
# TODO: Replace ChromaDB with graph DB - commenting out ChromaDB imports
# import os
# from uuid import uuid4
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings
# from langchain_chroma import Chroma
# from langchain_core.documents import Document
# from app.core.config import settings

logger = logging.getLogger(__name__)

# TODO: Replace ChromaDB with graph DB - commenting out global variables
# _embeddings = None
# _vector_store = None

# TODO: Replace ChromaDB with graph DB
# def _get_embeddings() -> OpenAIEmbeddings:
#     global _embeddings
#     if _embeddings is not None:
#         return _embeddings
#     try:
#         _embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
#         return _embeddings
#     except Exception as e:
#         logger.error(f"Failed to initialize OpenAIEmbeddings: {e}")
#         raise

# TODO: Replace ChromaDB with graph DB
# def _get_vector_store() -> Chroma:
#     global _vector_store
#     if _vector_store is not None:
#         return _vector_store
#     try:
#         persist_dir = settings.CHROMA_DB_PATH
#         os.makedirs(persist_dir, exist_ok=True)
#         _vector_store = Chroma(
#             collection_name="meeting_transcripts",
#             embedding_function=_get_embeddings(),
#             persist_directory=persist_dir,
#         )
#         return _vector_store
#     except Exception as e:
#         logger.error(f"Failed to initialize Chroma vector store: {e}")
#         raise

# TODO: Replace ChromaDB with graph DB
def add_transcript_to_db(meeting_id: str, transcript: str) -> None:
    """
    Placeholder function - ChromaDB functionality commented out.
    Will be replaced with graph DB implementation.
    """
    logger.info(f"Skipping vector DB storage for meeting {meeting_id} - will be replaced with graph DB")
    return
    # try:
    #     if not transcript:
    #         raise ValueError("Empty transcript")
    #     splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    #     chunks = splitter.split_text(transcript)
    #     if not chunks:
    #         raise ValueError("No chunks produced from transcript")
    #     docs: List[Document] = [
    #         Document(page_content=chunk, metadata={"meeting_id": meeting_id})
    #         for chunk in chunks
    #     ]
    #     ids: List[str] = [f"{meeting_id}_{i}_{uuid4()}" for i in range(len(docs))]
    #     _get_vector_store().add_documents(documents=docs, ids=ids)
    #     logger.info(f"Added {len(docs)} chunks for meeting {meeting_id}")
    # except Exception as e:
    #     logger.error(f"Failed adding transcript for meeting {meeting_id}: {e}")
    #     raise

# TODO: Replace ChromaDB with graph DB
def search_transcripts(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Placeholder function - ChromaDB functionality commented out.
    Will be replaced with graph DB implementation.
    Returns empty results for now.
    """
    logger.info(f"Vector search disabled - will be replaced with graph DB. Query: {query}")
    return []
    # try:
    #     if not query:
    #         return []
    #     results = _get_vector_store().similarity_search_with_score(query, k=top_k)
    #     formatted: List[Dict[str, Any]] = []
    #     for doc, score in results:
    #         formatted.append({
    #             "content": doc.page_content,
    #             "metadata": doc.metadata,
    #             "distance": score,
    #         })
    #     return formatted
    # except Exception as e:
    #     logger.error(f"Vector search failed for query '{query}': {e}")
    #     return []