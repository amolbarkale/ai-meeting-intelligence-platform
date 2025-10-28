import logging
import chromadb
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings

logger = logging.getLogger(__name__)

# --- Initialize ChromaDB Client ---
# This creates a persistent client that stores data on disk.
client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)

# --- Initialize the Embedding Function ---
# This uses a default, high-quality model to create vector embeddings.
# It will be downloaded automatically the first time it's used.
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction()

# --- Get or Create a Collection ---
# A collection is like a table in a database.
COLLECTION_NAME = "meeting_transcripts"
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=sentence_transformer_ef
)

def add_transcript_to_db(meeting_id: str, transcript: str):
    """
    Splits a transcript into chunks and adds them to the ChromaDB collection.
    """
    logger.info(f"Adding transcript for meeting {meeting_id} to vector DB.")
    
    # Use LangChain's text splitter for consistency
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(transcript)
    
    # Create unique IDs for each chunk
    chunk_ids = [f"{meeting_id}_{i}" for i in range(len(chunks))]
    
    # Add the chunks to the collection. The embedding is created automatically.
    collection.add(
        documents=chunks,
        metadatas=[{"meeting_id": meeting_id} for _ in chunks],
        ids=chunk_ids
    )
    logger.info(f"Successfully added {len(chunks)} chunks for meeting {meeting_id}.")

def search_transcripts(query: str, top_k: int = 5) -> list:
    """
    Searches the collection for the most relevant transcript chunks.
    """
    logger.info(f"Performing vector search for query: '{query}'")
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    # Format the results into a more usable structure
    search_results = []
    if results['documents']:
        for i, doc in enumerate(results['documents'][0]):
            search_results.append({
                "content": doc,
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i]
            })
    
    return search_results