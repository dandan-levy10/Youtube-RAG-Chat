from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from uuid import uuid4, UUID

class SummaryRequest(BaseModel):
    video_url: HttpUrl

class SummaryResponse(BaseModel):
    video_id: str
    summary: str

class ChatRequest(BaseModel):
    video_url: HttpUrl
    question: str

class ChatResponse(BaseModel):
    answer: str
