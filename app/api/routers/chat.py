from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from sqlmodel import Session
from uuid import uuid4
import logging

from app.services.rag import rag_chat_service
from app.models.schemas import ChatRequest, ChatResponse, LoadChatResponse
from app.services.transcription import extract_video_id
from db.session import get_session
from db.crud import load_history, save_message, load_summary

print("🟢 chat.py router loaded")


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix = "/chat",
    tags= ["chats"]
)

@router.post("/", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    response: Response,
    db: Session = Depends(get_session),
    user_id: str | None = Cookie(default=None)
    ):
    # retrieve or create session_id
    if user_id is None:
        user_id = str(uuid4())
        logger.debug(f"Created a new UUID: {user_id}")
        response.set_cookie(
            key="user_id",
            value=user_id,
            httponly=True,
            max_age=3600,
            samesite="strict",
            secure=False,
            path="/"
        )
        logger.debug(f"Assigned and set new user_id cookie: {user_id}")
    
    video_id = extract_video_id(request.video_url)
    
    # Load history from SQL DB 
    history = load_history(db, user_id, video_id)   # Retrieves List[ChatMessage]
    history = [(item.question, item.answer) for item in history]

    if not history:
        logger.debug("DB miss. History empty")
    else:
        logger.debug(f"DB hit. History: {history}")

    # Perform RAG QA call
    try:
        answer = rag_chat_service(
            video_url=str(request.video_url),
            question=request.question,
            history=history,
            db=db
            )
    except Exception as e:
        logger.exception("❌ rag_chat_service failed")
        raise HTTPException(status_code=502, detail=str(e)) from e

    # # Save Q&A DB
    save_message(db, request.question, answer, video_id, user_id)

    return ChatResponse(answer=answer)

@router.get("/user/{user_id}/conversations/{video_id}/get_history", response_model=LoadChatResponse)
def load_previous_conversation(
    user_id: str,
    video_id: str,
    db: Session = Depends(get_session)
):
    summary = load_summary(db=db, video_id=video_id)
    history = load_history(db=db, user_id=user_id, video_id=video_id)

    logger.info(f"Backend: user_id={user_id}, video_id={video_id}")
    logger.info(f"Backend: summary loaded: {summary is not None}")
    if summary:
        logger.info(f"Backend: summary title: {summary.title}")
    logger.info(f"Backend: history loaded, count: {len(history)}")

    response = LoadChatResponse(
        user_id=user_id,
        video_id=video_id,
        history=history,
        summary=summary
        )
    return response