import logging
from app.services.transcription import get_transcript
from app.services.chunking import chunk_documents
from app.services.embedding import embed_and_save
from app.core.logging_setup import setup_logging


setup_logging()

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    docs = get_transcript("https://www.youtube.com/watch?v=ZrK3L0IXb9c&ab_channel=TechWithTim")
    chunks = chunk_documents(documents=docs, chunk_size=1000,chunk_overlap=200)
    embed_and_save(documents=chunks)