from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from app.services.summariser import summarise_ingest
from app.services.transcription import extract_video_id

router = APIRouter(
    prefix="/summarize",
    tags=["summaries"]
)

class SummariseRequest(BaseModel):
    video_url: HttpUrl

class SummariseResponse(BaseModel):
    video_id: str
    summary: str

@router.post("/", response_model=SummariseResponse)
async def summarise_endpoint(request: SummariseRequest):
    try:
        summary_text = summarise_ingest(request.video_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail= str(e))
    video_id = extract_video_id(request.video_url)
    return SummariseResponse(summary=summary_text, video_id=video_id)

