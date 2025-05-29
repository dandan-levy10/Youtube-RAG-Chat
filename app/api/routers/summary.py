from fastapi import APIRouter, HTTPException, Depends
from app.services.summariser import summarise_ingest
from app.services.transcription import extract_video_id
from app.models.schemas import SummaryRequest, SummaryResponse
from db.session import get_session
from sqlmodel import Session
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/summarise",
    tags=["summaries"]
)

@router.post("/", response_model=SummaryResponse)
async def summarise_endpoint(request: SummaryRequest, db: Session = Depends(get_session)):
    video_url: str = str(request.video_url)
    try:
        summary_text = summarise_ingest(video_url, db)
    except Exception as e:
        logger.exception("Failed to summarise video %s", video_url)
        raise HTTPException(status_code=500, detail= str(e))
    
    video_id = extract_video_id(request.video_url)
    return SummaryResponse(summary=summary_text, video_id=video_id)

