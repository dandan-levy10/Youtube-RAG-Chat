from langchain_ollama import OllamaLLM
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from app.models.schemas import SummaryOut
import logging
from pathlib import Path
import json

from transcription import get_transcript, extract_video_id

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
TRANSCRIPT_CACHE_DIR =Path(__file__).parent.parent / "transcript_cache"
TRANSCRIPT_CACHE_DIR.mkdir(exist_ok=True)

def summarise_ingest(video_url: str, summary_cache_dir: Path = SUMMARY_CACHE_DIR, transcript_cache_dir: Path = TRANSCRIPT_CACHE_DIR) -> str:
    video_id = extract_video_id(video_url)
    summary_cache_dir.mkdir(parents=True, exist_ok=True) 
    summary_cache_path = summary_cache_dir / f"{video_id}.json"
    # transcript_cache_path = transcript_cache_dir / f"{video_id}.json"
    
    if summary_cache_path.exists():
        try:
            data = json.loads(summary_cache_path.read_text())
            summary = data["summary"]
        except (ValueError, KeyError):
            logger.warning("Cache corrupted, re-generating summary for %s", video_id)
        else:
            logger.info(f"Successfully retrieved summary for video '{data["metadata"]["title"]}' (id: {video_id}) from cache.")
            logger.debug(f"Summary sample: {summary[:200]}")
            return summary
    
    else:
        logger.debug("Summary not found in cache, retrieving transcript to summarise")
        docs = get_transcript(video_url=video_url) # Searches for cached transcript, otherwise downloads it
        summary = summarise_documents(docs)
        serializable = {"summary": summary, "metadata":docs[0].metadata}
        tmp = summary_cache_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(serializable))
        tmp.replace(summary_cache_path)
        logger.info(f"Cached summary at {summary_cache_path}")
        return summary
