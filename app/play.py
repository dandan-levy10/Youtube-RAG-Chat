import logging

from app.core.logging_setup import setup_logging
from app.services.rag import create_chat_session

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