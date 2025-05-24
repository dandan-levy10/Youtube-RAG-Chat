from langchain_ollama import OllamaLLM
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
import logging
from pathlib import Path
from sqlmodel import Session

from app.services.transcription import get_transcript, extract_video_id
from db.session import get_session
from db.crud import load_summary, save_summary


logger = logging.getLogger(__name__)

llm = OllamaLLM(
    model="llama3.2:latest",
    model_kwargs={
        "max_tokens": 16000,
        "temperature": 0.0,
    }
    )

def summarise_documents(documents: list[Document]) -> str:
    chain = load_summarize_chain(llm=llm, chain_type="stuff")
    summary = chain.invoke(input=documents)
    logger.info(f"Summarised transcript from video '{documents[0].metadata["title"]}'  documents using '{chain._chain_type}' chain type")
    logger.debug(f"Summary: {summary["output_text"]}")
    
    return summary["output_text"]

def length_function(documents: list[Document]) -> int:
    """Get number of tokens for input contents."""
    length = sum(llm.get_num_tokens(doc.page_content) for doc in documents)
    char_length = sum(len(doc.page_content) for doc in documents)
    logger.info(f"Total documents token length: {length}, char length {char_length}")
    # logger.info(f"Max input size: {llm.max_input_size}")
    return length 

SUMMARY_CACHE_DIR = Path(__file__).parent.parent / "summary_cache"
SUMMARY_CACHE_DIR.mkdir(exist_ok=True)

def summarise_ingest(video_url: str, db: Session) -> str:
    video_id = extract_video_id(video_url)
    
    # Try loading the existing record
    cached = load_summary(db, video_id)    # Optional[Summary]
    if cached is not None:
        return cached.summary
    
    # Cache miss → generate new summary
    logger.debug("Summary not found in cache, retrieving transcript to summarise")
    docs = get_transcript(video_url) # Searches for cached transcript, otherwise downloads it
    new_summary = summarise_documents(docs)
    
    # Persist for next time:
    save_summary(
        db=db,
        video_id=video_id,
        title=docs[0].metadata["title"],
        summary=new_summary,
        metadata=docs[0].metadata)
    
    return new_summary
