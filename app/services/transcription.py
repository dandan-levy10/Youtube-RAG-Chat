from langchain_community.document_loaders import YoutubeLoader
from yt_dlp import YoutubeDL # for metadata
from langchain.schema import Document
from urllib.parse import urlparse, parse_qs
from pydantic import HttpUrl
from sqlmodel import Session
import logging

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
      saves the full transcript in the DB, and returns the raw chunks.
    """

    video_id = extract_video_id(video_url)
    clean_url = f"https://www.youtube.com/watch?v={video_id}"
    
    # Try loading the existing record
    cache = load_transcript(db, video_id)
    if cache is not None:
        documents = [Document(
            metadata = cache.doc_metadata or {}, 
            page_content=cache.transcript)] # Single-item List[Document]
        return documents
    
    # Otherwise download transcript fresh:

    # Load transcript only
    loader = YoutubeLoader.from_youtube_url(clean_url)
    docs = loader.load()
    logger.info(f"Downloaded transcript for video {video_id} from Langchain YoutubeLoader")

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
    
    # Save the transcript to db
    save_transcript(
        db=db, 
        video_id=video_id, 
        title=metadata["title"], 
        transcript=full_text, 
        metadata=metadata
        )
    
    # Return List[Document]
    return docs


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    get_transcript(video_url="https://www.youtube.com/watch?v=ZrK3L0IXb9c&ab_channel=TechWithTim")
