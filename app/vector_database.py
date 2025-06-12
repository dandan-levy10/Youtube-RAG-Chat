import logging

import chromadb
from chromadb import ClientAPI
from langchain_chroma.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import settings

logger = logging.getLogger()

# TODO: replace Ollama embedding function with API call
# Initalise embedding function
def get_embedding_function():
    embedding_function = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=settings.GEMINI_API_KEY,
    )
    return embedding_function

# --- Globals to hold our single client and vector store instance ---
_db_client = None
_vector_store = None

def get_chroma_client() -> ClientAPI | None:
    """Returns a singleton instance of the ChromaDB HTTP client."""
    global _db_client
    if _db_client is None:
        logger.info("Initialising ChromaDB client...")
        _db_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT
        )
        return _db_client


def get_vector_store(embedding_function) -> Chroma | None:
    """
    Returns a singleton instance of the LangChain Chroma vector store,
    connected to our main persistent collection.
    """
    global _vector_store
    if _vector_store is None:
        logger.info("Initializing vector store...")

        # Create the client to connect to the ChromdaDB server
        client = get_chroma_client()
        
        # Create the LangChain vector store object, passing in the client and embedding function
        _vector_store = Chroma(
            client=client,
            collection_name="youtube_videos",
            embedding_function=embedding_function,
        )
    return _vector_store

def check_if_vectors_exist(video_id: str, vector_store: Chroma) -> bool:
    """
    Checks if vectors for a specific video_id already exist in the single collection.

    Args:
        video_id: The unique ID of the video to check for.

    Returns:
        True if at least one document with that video_id exists, False otherwise.
    """
    try:
        # Retrieve result corresponding to video_id
        result = vector_store.get(
            where= {"video_id": video_id},
            limit=1,
        )

        # Result includes document IDs
        found_ids = result.get("ids",[])
        logger.info(f"Vector check for {video_id}: Found {len(found_ids)} existing document(s).")
        return len(found_ids) > 0
    
    except Exception as e:
        # This could happen if the collection doesn't exist yet, etc.
        print(f"An error occurred during vector check for {video_id}: {e}")
        return False