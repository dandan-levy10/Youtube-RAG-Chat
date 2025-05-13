from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from app.services.summariser import summarise_ingest
from app.services.transcription import extract_video_id
from app.models.schemas import SummaryRequest, SummaryResponse

router = APIRouter(
    prefix="/summarize",
    tags=["summaries"]
)

@router.post("/", response_model=SummaryResponse)
async def summarise_endpoint(request: SummaryRequest):
    video_url: str = str(request.video_url)
    try:
        summary_text = summarise_ingest(video_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail= str(e))
    video_id = extract_video_id(request.video_url)
    return SummaryResponse(summary=summary_text, video_id=video_id)

