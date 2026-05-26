from fastapi import APIRouter, HTTPException
from app.schemas import DebateRequest, DebateResponse
from app.services.llm import call_llm_json, DEBATE_PROMPT, as_list
from app.services.text_processor import clean_text, truncate_text
from app.config import get_settings

router = APIRouter()


@router.post("/debate", response_model=DebateResponse)
async def debate_content(req: DebateRequest):
    if not req.page_content.strip():
        raise HTTPException(status_code=400, detail="Page content is empty")

    settings = get_settings()
    content = clean_text(req.page_content)
    content = truncate_text(content, settings.max_page_length)

    try:
        prompt = DEBATE_PROMPT.format(content=content)
        data = await call_llm_json(prompt)

        return DebateResponse(
            arguments_for=as_list(data.get("arguments_for")),
            arguments_against=as_list(data.get("arguments_against")),
            verdict=data.get("verdict", ""),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
