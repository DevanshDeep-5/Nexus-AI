"""
POST /summarize — TL;DR Summary Endpoint
------------------------------------------
Takes the full page content, cleans and truncates it, then asks the LLM
to produce a structured summary with key points, insights, and a takeaway.
"""

from fastapi import APIRouter, HTTPException
from app.schemas import SummarizeRequest, SummarizeResponse
from app.services.llm import call_llm_json, SUMMARIZE_PROMPT, as_list
from app.services.text_processor import clean_text, truncate_text
from app.config import get_settings

router = APIRouter()


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_page(req: SummarizeRequest):
    """Generate a TL;DR summary of the page content."""

    if not req.page_content.strip():
        raise HTTPException(status_code=400, detail="Page content is empty")

    settings = get_settings()

    # Clean noise and truncate to stay within token limits
    content = clean_text(req.page_content)
    content = truncate_text(content, settings.max_page_length)

    try:
        # Send to LLM and parse the structured JSON response
        prompt = SUMMARIZE_PROMPT.format(content=content)
        data = await call_llm_json(prompt)

        return SummarizeResponse(
            key_points=as_list(data.get("key_points")),
            insights=as_list(data.get("insights")),
            takeaway=data.get("takeaway", ""),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
