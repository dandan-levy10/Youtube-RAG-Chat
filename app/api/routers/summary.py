import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.backend_schemas import IngestedSummaryData, SummaryRequest
from app.services.summariser import summarise_ingest
from db.session import get_session
from shared.schemas import SummaryResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/summarise",
    tags=["summaries"]
)

@router.post("/", response_model=SummaryResponse)
async def summarise_endpoint(request: SummaryRequest, db: Session = Depends(get_session)):
    video_url: str = str(request.video_url)
    try:
        summary : IngestedSummaryData = summarise_ingest(video_url, db)
    except Exception as e:
        logger.exception("Failed to summarise video {video_url}, error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail= str(e))
    
    return SummaryResponse(summary=summary.summary, video_id=summary.video_id, title = summary.title)

