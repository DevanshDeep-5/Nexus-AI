"""
POST /eli5 — Explain Like I'm 5 Endpoint
-------------------------------------------
Simplifies complex page content into a beginner-friendly explanation
using simple words, analogies, and relatable examples.
"""

from fastapi import APIRouter, HTTPException
from app.schemas import ELI5Request, ELI5Response
from app.services.llm import call_llm_json, ELI5_PROMPT
from app.services.text_processor import clean_text, truncate_text
from app.config import get_settings

router = APIRouter()


@router.post("/eli5", response_model=ELI5Response)
async def explain_like_five(req: ELI5Request):
    """Simplify complex content into a beginner-friendly explanation."""

    if not req.page_content.strip():
        raise HTTPException(status_code=400, detail="Page content is empty")

    settings = get_settings()

    # Clean noise and truncate to stay within token limits
    content = clean_text(req.page_content)
    content = truncate_text(content, settings.max_page_length)

    try:
        prompt = ELI5_PROMPT.format(content=content)
        data = await call_llm_json(prompt)

        return ELI5Response(
            explanation=data.get("explanation", "Could not simplify the content."),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
