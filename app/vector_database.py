import chromadb
from langchain_chroma.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

from config import settings

# TODO: replace Ollama embedding function with API call
# Initalise embedding function
def get_embedding_function():
    embedding_function = OllamaEmbeddings(model="nomic-embed-text")
    return embedding_function

# A global variable to hold the vector store, so we only initialise it once 
_vector_store = None

def get_vector_store(embedding_function):
    """
    Initializes and returns a singleton instance of the LangChain Chroma
    vector store using the provided embedding function.

    NOTE: This lean version assumes you will use the SAME embedding
    function for the entire lifetime of the application.
    """
    global _vector_store

    if _vector_store is None:
        print("Initializing vector store...")

        # Create the client to connect to the ChromdaDB server
        client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT
        )
        
        # Create the LangChain vector store object, passing in the client and embedding function
        _vector_store = Chroma(
            client=client,
            collection_name="youtube_videos",
            embedding_function=embedding_function,
        )
    return _vector_store