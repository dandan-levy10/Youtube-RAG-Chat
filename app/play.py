import logging

from app.core.logging_setup import setup_logging
from app.services.chunking import chunk_documents
from app.services.embedding import embed_and_save
from app.services.rag import create_chat_session
from app.services.summariser import length_function, summarise_documents
from app.services.transcription import get_transcript

setup_logging(level=logging.DEBUG)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # docs = get_transcript("https://www.youtube.com/watch?v=C4P3XSySBC8&t=3265s&ab_channel=TheFreePress")
    # chunks = chunk_documents(documents=docs, chunk_size=1000,chunk_overlap=200)
    # embed_and_save(documents=chunks)
    # summary = summarise_documents(chunks)
    # length_function(chunks)
    session = create_chat_session()
    session.ask("What are the guests views on the Trump administration?")