import logging
from urllib.parse import parse_qs, urlparse

from langchain.schema import Document
from langchain_community.document_loaders import YoutubeLoader
from pydantic import HttpUrl
from sqlmodel import Session
from yt_dlp import YoutubeDL  # for metadata

from app.core.logging_setup import setup_logging
from db.crud import load_transcript, save_transcript

# Set up logger
setup_logging()

logger = logging.getLogger(__name__)


def extract_video_id(video_url: HttpUrl) -> str | None:
    # Normalise to a build-in str
    video_url = str(video_url)
    
    parsed = urlparse(video_url)
    # youtu.be/XYZ
    if parsed.netloc.endswith("youtu.be"):
        video_id = parsed.path.lstrip("/")
    # youtube.com/watch?v=XYZ
    else: 
        video_id = parse_qs(parsed.query).get("v", [None])[0]

    if not video_id:
        logger.error(f"Failed to extract video_id from URL: {video_url}")
        raise ValueError(f"Invalid Youtube URL, could not parse video_id: {video_url}")

    return str(video_id)


def get_transcript(video_url: str, db: Session) -> list[Document]:
    """
    Return a list of Document chunks for this video.
    - If cached in the DB, wraps that single transcript in one Document.
    - Otherwise, downloads via YoutubeLoader, enriches metadata,
      saves the full transcript in the DB, and returns the raw Document.
    """

    video_id = extract_video_id(video_url)
    clean_url = f"https://www.youtube.com/watch?v={video_id}"
    
    # Try loading the existing record
    cache = load_transcript(db, video_id)
    if cache is not None:
        documents = [
            Document(
            metadata = cache.doc_metadata or {}, 
            page_content=cache.transcript
            )
            ] # Single-item List[Document]
        return documents
    
    logger.info(f"Transcript not in cache for {video_id}. Fetching from YouTube via LangChain loader.")
    
    # Otherwise download transcript fresh:

    # Load transcript only
    loader = YoutubeLoader.from_youtube_url(clean_url)
    try:
        # Assuming you instantiate your LangChain loader like this:
        # from langchain_community.document_loaders import YoutubeLoader
        # loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=True, language=['en', 'id'], translation='en')
        # For simplicity, let's assume loader is defined/imported

        docs = loader.load() # This is the line that fails in the traceback

        if not docs:
            logger.warning(f"LangChain loader returned no documents for video_url: {video_url} (video_id: {video_id}). This might mean no transcript was found or an issue occurred.")
            # You might want to raise a specific error or return an empty list
            # depending on how summarise_ingest should handle this.
            # For now, let's allow summarise_ingest to handle an empty list if that's its design.
            return [] # Return empty list if no transcript docs found

        logger.info(f"Successfully fetched {len(docs)} transcript document(s) for video_id: {video_id} from Langchain YoutubeLoader")
        # # 2. Save the fetched transcript to your DB cache here
        # # save_transcript_to_db(db, video_id, docs, ...) # (You'll need to implement this)
        # return docs

    except Exception as e: # Catch specific exceptions from youtube_transcript_api if known, or general Exception
        logger.error(f"Failed to load transcript using LangChain loader for URL {video_url} (video_id: {video_id}): {type(e).__name__} - {e}", exc_info=True)
        # Option 1: Re-raise a custom error that summarise_endpoint can catch and give a nice message
        # raise ValueError(f"Could not retrieve or process transcript for the video: {video_url}. Please check the URL or try another video.") from e
        # Option 2: Return an empty list and let downstream functions handle it
        return []


    # fetch video metadata via yt-dlp
    ydl_opts = {"quiet": True, "skip_download": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False) # get metadata, don't dl video/audio
    logger.info(f"Downloaded {info.get("title")} video metadata from yt-dlp")

    # Add information to documents' metadata
    base_meta = {
            "title":       info.get("title"),
            "uploader":    info.get("uploader"),
            "upload_date": info.get("upload_date"),
            "video_id":    video_id,
        }
    
    for doc in docs:
        doc.metadata.update(base_meta)

    # In case chunked documents returned, combine into one full transcript text
    full_text = "\n\n".join(doc.page_content for doc in docs)
    metadata = docs[0].metadata
    title = metadata.get("title", f"Title not available for {video_id}")
    
    # Save the transcript to db
    save_transcript(
        db=db, 
        video_id=video_id, 
        title=title, 
        transcript=full_text, 
        metadata=metadata
        )
    
    # Return List[Document]
    return docs


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    get_transcript(video_url="https://www.youtube.com/watch?v=ZrK3L0IXb9c&ab_channel=TechWithTim")
