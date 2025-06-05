from pydantic import BaseModel, HttpUrl
from db.models import ChatMessage, Summary

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

class PreviousConversationItem(BaseModel):
    video_id: str
    title: str

class PreviousConversationsResponse(BaseModel):
    conversations: list[PreviousConversationItem]

class SessionInitData(BaseModel):
    user_id: str
    is_new_user: bool

class LoadChatResponse(BaseModel):
    user_id: str
    video_id: str
    history: list[ChatMessage]
    summary: Summary
