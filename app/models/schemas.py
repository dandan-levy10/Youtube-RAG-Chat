from pydantic import BaseModel, HttpUrl, Field
from uuid import uuid4, UUID

class SummaryRequest(BaseModel):
    video_url: HttpUrl

class SummaryResponse(BaseModel):
    video_id: str
    summary: str

class ChatRequest(BaseModel):
    sid: UUID = Field(default_factory=uuid4)
    video_url: HttpUrl
    question: str
    # history: list[tuple[str,str]] = []

class ChatResponse(BaseModel):
    answer: str
    history: list[tuple[str,str]]