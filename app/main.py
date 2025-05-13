from core.logging_setup import setup_logging
from fastapi import FastAPI
from app.api.routers.summary import router as summary_router

app = FastAPI(
    title="Youtube RAG Chat",
    version= "0.1.0"
)

# mount router under /api
app.include_router(summary_router, prefix="/api")

if __name__ == "__main__":
    setup_logging()