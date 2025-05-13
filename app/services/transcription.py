import json
from pathlib import Path
from langchain_community.document_loaders import YoutubeLoader
from yt_dlp import YoutubeDL # for metadata
from langchain.schema import Document
from urllib.parse import urlparse, parse_qs
from pydantic import HttpUrl
import logging
from app.core.logging_setup import setup_logging

setup_logging()

logger = logging.getLogger(__name__)


CACHE_DIR = Path(__file__).parent.parent / "transcript_cache"
CACHE_DIR.mkdir(exist_ok=True)


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

    return video_id

# def clean_youtube_url(url: str) -> str:
#     p = urlparse(url)
#     params = parse_qs(p.query)
#     vid = params.get("v", [None])[0]
#     return f"https://www.youtube.com/watch?v={vid}" if vid else url

def get_transcript(video_url: str) -> list[Document]:
    video_id = extract_video_id(video_url)
    cache_path = CACHE_DIR / f"{video_id}.json"
    if cache_path.exists():
        data = json.loads(cache_path.read_text())
        docs = [Document(metadata = doc["metadata"], page_content= doc["page_content"]) for doc in data]
        logger.info(f"Successfully retrieved transcript for video '{docs[0].metadata["title"]}' (id: {video_id}) from cache.")
        logger.debug(f"Document sample: {docs[0].page_content[:200]}")

        return docs

    # Load transcript only
    loader = YoutubeLoader.from_youtube_url(video_url)
    docs = loader.load()
    logger.info("Downloaded transcript for video {video_id} from Langchain YoutubeLoader")

    # fetch video metadata via yt-dlp
    ydl_opts = {"quiet": True, "skip_download": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False) # get metadata, don't dl video/audio
    logger.info(f"Downloaded {info.get("title")} video metadata from yt-dlp")

    for doc in docs:
        doc.metadata["title"] = info.get("title")
        doc.metadata["uploader"] = info.get("uploader")
        doc.metadata["upload_date"] = info.get("upload_date")

    serializable = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs]
    cache_path.write_text(json.dumps(serializable))
    logger.debug(f"Document sample: {docs[0].page_content[:200]}")
    return docs

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    get_transcript(video_url="https://www.youtube.com/watch?v=ZrK3L0IXb9c&ab_channel=TechWithTim")
