import logging
from typing import TypedDict, cast

from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from langchain_ollama import OllamaLLM
from sqlmodel import Session

from app.backend_schemas import IngestedSummaryData
from app.services.transcription import extract_video_id, get_transcript
from db.crud import load_summary, save_summary

logger = logging.getLogger(__name__)

llm = OllamaLLM(
    model="llama3.2:latest",
    temperature=0.0,
    num_predict=256, # Max tokens to predict when generating text
    )

class SummaryChainOutput(TypedDict):
    output_text: str

def summarise_documents(documents: list[Document]) -> str:
    chain = load_summarize_chain(llm=llm, chain_type="stuff")
    summary: SummaryChainOutput = cast(SummaryChainOutput, chain.invoke({"input_documents":documents}))
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

def summarise_ingest(video_url: str, db: Session) -> IngestedSummaryData:
    video_id = extract_video_id(video_url)
    
    # Try loading the existing record
    cached = load_summary(db, video_id)    # Optional[Summary]
    if cached is not None:
        return IngestedSummaryData(video_id=cached.video_id, summary=cached.summary, title=cached.title)
    
    # Cache miss → generate new summary
    logger.debug("Summary not found in cache, retrieving transcript to summarise")
    docs = get_transcript(video_url, db) # Searches for cached transcript, otherwise downloads it

    if not docs: 
        logger.warning(f"No transcript documents available for summarization for URL: {video_url}")
        # Raise an error to be caught by the endpoint
        raise ValueError(f"Cannot summarize video: No transcript found or processed for {video_url}.")

    new_summary = summarise_documents(docs)
    title = docs[0].metadata["title"]
    # Persist for next time:
    save_summary(
        db=db,
        video_id=video_id,
        title=title,
        summary=new_summary,
        metadata=docs[0].metadata)
    
    return IngestedSummaryData(
        video_id=video_id,
        summary=new_summary,
        title=title)
