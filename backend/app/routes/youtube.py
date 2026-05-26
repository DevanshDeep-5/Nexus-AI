from fastapi import APIRouter, HTTPException
from app.schemas import YouTubeTranscriptRequest, YouTubeTranscriptResponse
from app.services.youtube import fetch_transcript

router = APIRouter()


@router.post("/youtube/transcript", response_model=YouTubeTranscriptResponse)
async def get_youtube_transcript(req: YouTubeTranscriptRequest):
    if not req.video_id.strip():
        raise HTTPException(status_code=400, detail="Video ID is empty")

    try:
        transcript = fetch_transcript(req.video_id)
        return YouTubeTranscriptResponse(
            transcript=transcript,
            video_id=req.video_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
