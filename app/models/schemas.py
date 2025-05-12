from pydantic import BaseModel

class SummaryOut(BaseModel):
    video_id: str
    summary: str

class ChatRequest(BaseModel):
    question: str
    history: list[tuple[str,str]] = []

class ChatResponse(BaseModel):
    answer: str
    history: list[tuple[str,str]]