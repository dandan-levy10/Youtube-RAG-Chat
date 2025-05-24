from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from uuid import uuid4
from datetime import datetime, timezone

class ChatMessage(SQLModel, table = True):
    id: str = Field(default_factory= lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    video_id: str = Field(index=True)
    question: str
    answer: str
    created_at: datetime = Field(default_factory= lambda: datetime.now(timezone.utc), index=True)

class Transcript(SQLModel, table=True):
    video_id: str = Field(primary_key=True)
    title: str
    transcript: str
    metadata: dict = Field(sa_column=Column(JSONB))

class Summary(SQLModel, table=True):
    video_id: str = Field(primary_key=True)
    title: str    
    summary: str 
    metadata: dict = Field(sa_column=Column(JSONB))


