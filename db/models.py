from sqlmodel import SQLModel, Field
from uuid import uuid4
from datetime import datetime, timezone

class ChatMessage(SQLModel, table = True):
    id: str = Field(default_factory= lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    video_id: str = Field(index=True)
    question: str
    answer: str
    created_at: datetime = Field(default_factory= lambda: datetime.now(timezone.utc), index=True)