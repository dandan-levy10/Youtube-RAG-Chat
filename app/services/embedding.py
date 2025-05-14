# from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_ollama import OllamaEmbeddings
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma 
import logging

logger = logging.getLogger(__name__)

# Silence Chroma’s telemetry banner
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.WARNING)

# Silence httpx request/response logs (used by Chroma under the hood)
logging.getLogger("httpx").setLevel(logging.WARNING)

# initalise embedding function
def get_embedding_function():
    embedding_function = OllamaEmbeddings(model="nomic-embed-text")
    return embedding_function
 

def embed_and_save(documents):
    embedding_function = OllamaEmbeddings(model="nomic-embed-text")
    
    vectordb = Chroma(
        embedding_function= embedding_function,
        persist_directory="app/chroma_db"
        )
    logger.info(f"Connected to ChromaDB {vectordb._persist_directory}")

    # extract the raw text and any existing metadata
    # texts    = [doc.page_content for doc in documents]
    metas    = [doc.metadata for doc in documents]
    ids      = [f"{doc.metadata["video_id"]}-{i}" for i, doc in enumerate(documents)]
    
    vectordb.add_documents(
        documents=documents,
        metadata = metas,
        ids=ids)
    logger.info(f"Added {len(documents)} documents to {vectordb._persist_directory}")
    # vectordb.persist()