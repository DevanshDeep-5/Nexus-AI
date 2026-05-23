"""
POST /youtube/transcript — YouTube Transcript Extraction Endpoint
--------------------------------------------------------------------
Fetches the transcript (auto-captions or manual subtitles) of a YouTube
video by its video ID. The transcript can then be used as page content
for summarization, Q&A, or notes generation.
"""

from fastapi import APIRouter, HTTPException
from app.schemas import YouTubeTranscriptRequest, YouTubeTranscriptResponse
from app.services.youtube import fetch_transcript

router = APIRouter()


@router.post("/youtube/transcript", response_model=YouTubeTranscriptResponse)
async def get_youtube_transcript(req: YouTubeTranscriptRequest):
    """Fetch the transcript of a YouTube video."""

    if not req.video_id.strip():
        raise HTTPException(status_code=400, detail="Video ID is empty")

    try:
        transcript = fetch_transcript(req.video_id)
        return YouTubeTranscriptResponse(
            transcript=transcript,
            video_id=req.video_id,
        )
    except ValueError as e:
        # ValueError is raised when the transcript can't be found
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
