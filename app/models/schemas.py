from pydantic import BaseModel, HttpUrl

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