"""
POST /curiosity — Smart Curiosity Suggestions Endpoint
--------------------------------------------------------
Generates insightful follow-up questions about the page content
that a curious reader might want to explore further.
These are displayed as suggestion chips in the Chat tab.
"""

from fastapi import APIRouter, HTTPException
from app.schemas import CuriosityRequest, CuriosityResponse
from app.services.llm import call_llm_json, CURIOSITY_PROMPT, as_list
from app.services.text_processor import clean_text, truncate_text
from app.config import get_settings

router = APIRouter()


@router.post("/curiosity", response_model=CuriosityResponse)
async def curiosity_suggestions(req: CuriosityRequest):
    """Generate smart follow-up questions about the page content."""

    if not req.page_content.strip():
        raise HTTPException(status_code=400, detail="Page content is empty")

    settings = get_settings()

    # Clean noise and truncate to stay within token limits
    content = clean_text(req.page_content)
    content = truncate_text(content, settings.max_page_length)

    try:
        prompt = CURIOSITY_PROMPT.format(content=content)
        data = await call_llm_json(prompt)

        if data.get("error"):
            raise HTTPException(status_code=502, detail=str(data.get("error")))

        return CuriosityResponse(
            questions=as_list(data.get("questions")),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
