from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from app.services.rag import rag_chat_service
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter(
    prefix = "/chat",
    tags= ["chats"]
)