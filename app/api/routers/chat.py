from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
import redis
from uuid import uuid4

from app.services.rag import rag_chat_service
from app.models.schemas import ChatRequest, ChatResponse

_redis_client = redis.Redis(host="localhost", port=6379, db=0)

def get_redis():
    # FastAPI dependency that returns singleton Redis Client
    return _redis_client


router = APIRouter(
    prefix = "/chat",
    tags= ["chats"]
)

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, redis = Depends(get_redis)):
    # retrieve or create session_id
    sid = request.session_id or str(uuid4())
