from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)


def chunk_documents(documents: list[Document], chunk_size: int, chunk_overlap: int) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        length_function = len,
    )
    docs = text_splitter.split_documents(documents=documents)
    logger.info(f"Split document '{docs[0].metadata["title"]}' into {len(docs)} chunks")
    logger.debug(f"Chunk samples: {docs[:2]}")
    return docs