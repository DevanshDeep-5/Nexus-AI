"""
POST /keypoints — Extract Key Points Endpoint
-------------------------------------------------
Extracts the most important key points from the page content
and returns them as a structured list.
"""

from fastapi import APIRouter, HTTPException
from app.schemas import KeypointsRequest, KeypointsResponse
from app.services.llm import call_llm_json, KEYPOINTS_PROMPT, as_list
from app.services.text_processor import clean_text, truncate_text
from app.config import get_settings

router = APIRouter()


@router.post("/keypoints", response_model=KeypointsResponse)
async def extract_keypoints(req: KeypointsRequest):
    """Extract key points from the page content."""

    if not req.page_content.strip():
        raise HTTPException(status_code=400, detail="Page content is empty")

    settings = get_settings()

    # Clean noise and truncate to stay within token limits
    content = clean_text(req.page_content)
    content = truncate_text(content, settings.max_page_length)

    try:
        prompt = KEYPOINTS_PROMPT.format(content=content)
        data = await call_llm_json(prompt)

        return KeypointsResponse(
            keypoints=as_list(data.get("keypoints")),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
