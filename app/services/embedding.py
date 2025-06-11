import logging

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from app.vector_database import get_embedding_function

logger = logging.getLogger(__name__)

# Silence Chroma’s telemetry banner
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.WARNING)

# Silence httpx request/response logs (used by Chroma under the hood)
logging.getLogger("httpx").setLevel(logging.WARNING)


 

def embed_and_save(documents):
    embedding_function = get_embedding_function() # Returns nomic-embed Ollama embeddings model
    
    vectordb = Chroma(
        embedding_function= embedding_function,
        persist_directory="app/chroma_db"
        )
    logger.info(f"Connected to ChromaDB {vectordb._persist_directory}")

    metas = [doc.metadata for doc in documents]
    ids = [f"{doc.metadata["video_id"]}-{i}" for i, doc in enumerate(documents)]
    
    vectordb.add_documents(
        documents=documents,
        metadata = metas,
        ids=ids)
    logger.info(f"Added {len(documents)} documents to {vectordb._persist_directory}")
