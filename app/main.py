import logging
from app.core.logging_setup import configure_logging
# Set up logging
configure_logging(level = 10)

logger = logging.getLogger()

from app.api.routers.summary import router as summary_router
from app.api.routers.chat import router as chat_router
from db.session import engine
from app.models.schemas import PreviousConversationsRequest, PreviousConversationsResponse
from db.crud import get_video_ids_and_titles_by_user_id
from db.session import get_session

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Session

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Before startup:
    SQLModel.metadata.create_all(engine) # Create all tables
    yield
    # After startup:


app = FastAPI(
    title="Youtube RAG Chat",
    version= "0.1.0",
    lifespan=lifespan, 
    debug=True
)

# configure_logging(level=logging.DEBUG)
# logging.getLogger("httpx").setLevel(logging.WARNING)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:8501"], # Trust front-end on port 8501
    allow_methods = ["*"],                     # HTTP actions/ verbs permitted
    allow_headers = ["*"],                     # HTTP headers permitted
    allow_credentials=True                     # Allow sending credentials (includes cookies)
)

# mount router under /api
app.include_router(summary_router, prefix="/api")
app.include_router(chat_router, prefix="/api")

@app.get("/previous_conversations/{user_id}", response_model=PreviousConversationsResponse)
def get_past_conversations(
    user_id: str,
    db: Session = Depends(get_session), 
    ) -> list[tuple[str,str]]:
    try:
        results = get_video_ids_and_titles_by_user_id(db=db, target_user_id=user_id)
    except Exception as e:
        logger.exception("❌ rag_chat_service failed")
        raise HTTPException(status_code=502, detail=str(e)) from e
    
    # Convert to PreviousConversationsResponse pydantic model
    response_list = [PreviousConversationsResponse(video_id=video_id, title=title) for video_id, title in results]
    return response_list


if __name__ == "__main__":
    from app.core.logging_setup import configure_logging
    import uvicorn
    

    uvicorn.run(
        app="app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None
    )