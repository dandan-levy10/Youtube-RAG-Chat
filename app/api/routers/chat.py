import logging
from uuid import uuid4

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlmodel import Session

from app.backend_schemas import ChatMessage, ChatRequest, LoadChatResponse
from app.services.rag import rag_chat_service
from app.services.transcription import extract_video_id
from db.crud import load_history, load_summary, save_message
from db.session import get_session
from shared.schemas import ChatResponse

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
    # TODO: manage exceptions more robustly here
    try:
        # # --- ALL OF YOUR ORIGINAL CODE GOES INSIDE THIS TRY BLOCK ---
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
        
        video_id = extract_video_id(str(request.video_url)) # convert HttpUrl to str
        
        # This is the guard clause. We handle the "None" case here.
        if video_id is None:
            # If we can't get a video_id, we can't proceed.
            # It's best to stop and return an error to the user.
            raise HTTPException(
                status_code=400, 
                detail="Could not extract a valid video ID from the provided URL."
            )
        
        # Load history from SQL DB 
        chat_history_objects: list[ChatMessage] = load_history(db, user_id, video_id)   # Retrieves List[ChatMessage]
        history: list[tuple[str, str]] = [(item.question, item.answer) for item in chat_history_objects]

        if not history:
            logger.debug("DB miss. History empty")
        else:
            logger.debug(f"DB hit. History: {history}")

        # Perform RAG QA call
        # try:
        answer = rag_chat_service(
            video_url=str(request.video_url),
            question=request.question,
            history=history,
            db=db
            )
        # except Exception as e:
        #     logger.exception("❌ rag_chat_service failed")
        #     raise HTTPException(status_code=502, detail=str(e)) from e
    
    except Exception as e:
        # This will catch ANY error from anywhere in the function
        print(f"!!! A FATAL ERROR OCCURRED IN chat_endpoint: {e}", flush=True)
        
        # This will print the full, multi-line traceback we need to see
        traceback.print_exc() 
        
        # Raise a proper HTTP error
        raise HTTPException(
            status_code=500,
            detail=f"An internal error occurred: {e}"
        )

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