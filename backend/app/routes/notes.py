"""
POST /notes — Auto Notes Generator Endpoint
----------------------------------------------
Converts webpage content into well-structured study notes with
titled sections, bullet points, and highlighted key terms.
"""

from fastapi import APIRouter, HTTPException
from app.schemas import NotesRequest, NotesResponse, NotesSection
from app.services.llm import call_llm_json, NOTES_PROMPT, as_list
from app.services.text_processor import clean_text, truncate_text
from app.config import get_settings

router = APIRouter()


@router.post("/notes", response_model=NotesResponse)
async def generate_notes(req: NotesRequest):
    """Convert webpage content into structured notes."""

    if not req.page_content.strip():
        raise HTTPException(status_code=400, detail="Page content is empty")

    settings = get_settings()

    # Clean noise and truncate to stay within token limits
    content = clean_text(req.page_content)
    content = truncate_text(content, settings.max_page_length)

    try:
        prompt = NOTES_PROMPT.format(content=content)
        data = await call_llm_json(prompt)

        # Parse each section from the LLM's JSON response into NotesSection models
        sections = []
        for s in as_list(data.get("sections")):
            if not isinstance(s, dict):
                continue
            sections.append(NotesSection(
                heading=s.get("heading", ""),
                bullets=as_list(s.get("bullets")),
                key_terms=as_list(s.get("key_terms")),
            ))

        return NotesResponse(
            title=data.get("title", "Notes"),
            sections=sections,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
