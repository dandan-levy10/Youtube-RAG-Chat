from sqlmodel import Session, select
from db.models import ChatMessage
from typing import List

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