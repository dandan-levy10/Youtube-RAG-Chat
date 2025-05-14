from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from pydantic import BaseModel, HttpUrl
import redis
import redis.asyncio as aioredis
from uuid import uuid4
import json
import logging

from app.services.rag import rag_chat_service
from app.models.schemas import ChatRequest, ChatResponse
from app.services.transcription import extract_video_id

print("🟢 chat.py router loaded")


logger = logging.getLogger(__name__)

def get_redis():
    # FastAPI dependency that returns singleton Redis Client
    return aioredis.from_url("redis://localhost:6379/0")


router = APIRouter(
    prefix = "/chat",
    tags= ["chats"]
)

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    response: Response,
    redis = Depends(get_redis),
    session_id: str | None = Cookie(default=None)
    ):
    # retrieve or create session_id
    if session_id is None:
        session_id = str(uuid4())
        logger.debug(f"Created a new UUID: {session_id}")
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            max_age=3600,
            samesite="strict",
            secure=True,
            path="/"
        )
        logger.debug(f"Set cookie in response")
    
    video_id = extract_video_id(request.video_url)
    # Load history from Redis using session_id + video_id
    history_key = f"chat:{session_id}:{video_id}:history"
    raw = await redis.lrange(history_key, 0, -1) # Get all results matching key
    history = [json.loads(x) for x in raw] # Deserialise 
    if not history:
        logger.debug("Cache miss. History empty")
    else:
        logger.debug(f"Cache hit. History: {history}")

    # Perform RAG QA call
    try:
        answer = rag_chat_service(
            video_url=str(request.video_url),
            question=request.question,
            history=history
            )
    except Exception as e:
        logger.exception("❌ rag_chat_service failed")
        raise HTTPException(status_code=502, detail=str(e)) from e

    # Upload Q&A to redis
    await redis.rpush(history_key, json.dumps([request.question, answer]))
    await redis.expire(history_key, 3600)

    return ChatResponse(answer=answer)



    

