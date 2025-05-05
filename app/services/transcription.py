import json
from pathlib import Path
from langchain_community.document_loaders import YoutubeLoader
from yt_dlp import YoutubeDL # for metadata
from langchain.schema import Document
import logging
from app.core.logging_setup import setup_logging

setup_logging()

logger = logging.getLogger(__name__)


CACHE_DIR = Path(__file__).parent.parent / "transcript_cache"
CACHE_DIR.mkdir(exist_ok=True)

# from urllib.parse import urlparse, parse_qs

# def clean_youtube_url(url: str) -> str:
#     p = urlparse(url)
#     params = parse_qs(p.query)
#     vid = params.get("v", [None])[0]
#     return f"https://www.youtube.com/watch?v={vid}" if vid else url

def get_transcript(video_url: str) -> list[Document]:
    video_id = video_url.split("v=")[-1]
    cache_path = CACHE_DIR / f"{video_id}.json"
    if cache_path.exists():
        # print("retrieving from cache....")
        data = json.loads(cache_path.read_text())
        docs = [Document(metadata = doc["metadata"], page_content= doc["page_content"]) for doc in data]
        logger.info(f"Successfully retrieved transcript for video '{docs[0].metadata["title"]}' (id: {video_id}) from cache.")
        logger.debug(f"Document sample: {docs[0].page_content[:200]}")
        # print(docs)
        # print(docs[0].page_content)
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
    # video_meta = {
    #     "title": info.get("title"),
    #     "uploader": info.get("uploader"), 
    #     "upload_date": info.get("upload_date"),
    # }

    for doc in docs:
        doc.metadata["title"] = info.get("title")
        doc.metadata["uploader"] = info.get("uploader")
        doc.metadata["upload_date"] = info.get("upload_date")

    serializable = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs]
    cache_path.write_text(json.dumps(serializable))
    # print(docs[0].page_content)
    logger.debug(f"Document sample: {docs[0].page_content[:200]}")
    # print(docs)
    return docs

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    get_transcript("https://www.youtube.com/watch?v=ZrK3L0IXb9c&ab_channel=TechWithTim")
