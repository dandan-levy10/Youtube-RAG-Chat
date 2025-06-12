import logging

from app.vector_database import get_embedding_function, get_vector_store

logger = logging.getLogger(__name__)

# Silence Chroma’s telemetry banner
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.WARNING)

# Silence httpx request/response logs (used by Chroma under the hood)
logging.getLogger("httpx").setLevel(logging.WARNING)


def embed_and_save(documents):
    embedding_function = get_embedding_function() # Returns nomic-embed Ollama embeddings model
    
    vectordb = get_vector_store(embedding_function)
    logger.info(f"Connected to ChromaDB {vectordb._persist_directory}")

    metas = [doc.metadata for doc in documents]
    ids = [f"{doc.metadata["video_id"]}-{i}" for i, doc in enumerate(documents)]
    
    vectordb.add_documents(
        documents=documents,
        metadata = metas,
        ids=ids)
    logger.info(f"Added {len(documents)} documents to {vectordb._persist_directory}")
