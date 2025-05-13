from pydantic import BaseModel, HttpUrl

class SummaryRequest(BaseModel):
    video_url: HttpUrl

class SummaryResponse(BaseModel):
    video_id: str
    summary: str

class ChatRequest(BaseModel):
    question: str
    history: list[tuple[str,str]] = []

class ChatResponse(BaseModel):
    answer: str
    history: list[tuple[str,str]]