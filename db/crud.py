from sqlmodel import Session, select
from db.models import ChatMessage, Summary, Transcript
from typing import List
import logging

logger = logging.getLogger(__name__)


# ChatMessage table:

def save_message(db: Session, question: str, answer: str, video_id: str, user_id: str) -> ChatMessage:
    message = ChatMessage(question=question, answer=answer, user_id=user_id, video_id=video_id)
    db.add(message)
    db.commit()
    db.refresh(message)
    logger.debug(f"Successfully saved message for video id {video_id}.")
    return message

def load_history(db: Session, user_id: str, video_id: str) -> List[ChatMessage]:
    statement = select(ChatMessage).where(
        ChatMessage.user_id == user_id,
        ChatMessage.video_id == video_id
    ).order_by(ChatMessage.created_at)
    history = db.exec(statement).all()
    if history:
        logger.debug(f"Successfully loaded history for video id {ChatMessage.video_id}.")
    else:
        logger.debug(f"No history found for video id {video_id}.")
    return history

# Summary table:

def save_summary(db: Session, video_id: str, title: str, summary: str, metadata: dict) -> Summary:
    summary = Summary(
        video_id=video_id,
        title=title,
        summary=summary,
        doc_metadata=metadata
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)
    logger.debug(f"Successfully saved summary for video {title}; video id {video_id}.")
    return summary

def load_summary(db: Session, video_id: str) -> Summary | None:
    summary = db.get(Summary, video_id)
    if summary is None:
        logger.debug(f"No summary found for video {video_id}.")
    else:
        logger.debug(f"Successfully loaded transcript for video {summary.title}; video id {summary.video_id}.")
    return summary

# Transcript table:

def save_transcript(db: Session, video_id: str, title: str, transcript: str, metadata: dict) -> Transcript:
    transcript = Transcript(
        video_id=video_id,
        title=title,
        transcript=transcript,
        doc_metadata=metadata,       # ← keyword matches field name
    )
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    logger.debug(f"Successfully saved transcript for video {title}; video id {video_id}.")
    return transcript

def load_transcript(db: Session, video_id: str) -> Transcript | None:
    transcript = db.get(Transcript, video_id)
    if transcript is None:
        logger.debug(f"No transcript found for video {video_id}.")
    else:
        logger.debug(f"Successfully loaded transcript for video {transcript.title}; video id {transcript.video_id}.")
    return transcript