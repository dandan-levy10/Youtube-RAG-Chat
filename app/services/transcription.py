from langchain_community.document_loaders import YoutubeLoader

def get_transcript(url: str):
    loader = YoutubeLoader.from_youtube_url(url)
    transcript = loader.load()
    return transcript
