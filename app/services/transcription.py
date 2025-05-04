import json
from pathlib import Path
from langchain_community.document_loaders import YoutubeLoader
from langchain.schema import Document

CACHE_DIR = Path(__file__).parent.parent / "transcript_cache"
CACHE_DIR.mkdir(exist_ok=True)

def get_transcript(video_url: str) -> list[Document]:
    video_id = video_url.split("v=")[-1]
    cache_path = CACHE_DIR / f"{video_id}.json"
    if cache_path.exists():
        data = json.loads(cache_path.read_text())
        docs = [Document(metadata = doc["metadata"], page_content= doc["page_content"]) for doc in data]
        return docs

    loader = YoutubeLoader.from_youtube_url(video_url)
    docs = loader.load()
    serializable = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs]
    cache_path.write_text(json.dumps(serializable))
    print(docs[0].page_content)
    return docs

if __name__ == "__main__":
    get_transcript("https://www.youtube.com/watch?v=pmAseUOEB_s&ab_channel=sniffglue")
