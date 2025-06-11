from pydantic import BaseModel, HttpUrl

# Shared models have zero backend dependencies
    
class SummaryResponse(BaseModel):
    video_id: str
    summary: str
    title: str

class ChatResponse(BaseModel):
    answer: str

