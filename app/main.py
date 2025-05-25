from app.core.logging_setup import setup_logging
from app.api.routers.summary import router as summary_router
from app.api.routers.chat import router as chat_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from db.session import engine



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


if __name__ == "__main__":
    setup_logging()