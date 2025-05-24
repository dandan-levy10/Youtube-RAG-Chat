from sqlmodel import Session, select
from db.models import ChatMessage, Summary, Transcript
from typing import List


# ChatMessage table:

def save_message(db: Session, question: str, answer: str, video_id: str, user_id: str) -> ChatMessage:
    message = ChatMessage(question=question, answer=answer, user_id=user_id, video_id=video_id)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def load_history(db: Session, user_id: str, video_id: str) -> List[ChatMessage]:
    statement = select(ChatMessage).where(
        ChatMessage.user_id == user_id,
        ChatMessage.video_id == video_id
    ).order_by(ChatMessage.created_at)
    return db.exec(statement).all()

# Summary table:

def save_summary(db: Session, video_id: str, title: str, summary: str, metadata: dict) -> Summary:
    summary = Summary(video_id, title, summary, metadata)
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary

def load_summary(db: Session, video_id: str) -> Summary:
    statement = select(Summary).where(Summary.video_id == video_id)
    return db.exec(statement).all()

# Transcript table:

def save_transcript(db: Session, video_id: str, title: str, transcript: str, metadata: dict) -> Transcript:
    transcript = Transcript(video_id, title, transcript, metadata)
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return transcript

def load_transcript(db: Session, video_id: str) -> Transcript:
    statement = select(Transcript).where(video_id==video_id)
    return db.exec(statement).all()