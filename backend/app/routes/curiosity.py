from fastapi import APIRouter, HTTPException
from app.schemas import CuriosityRequest, CuriosityResponse
from app.services.llm import call_llm_json, CURIOSITY_PROMPT, as_list
from app.services.text_processor import clean_text, truncate_text
from app.config import get_settings

router = APIRouter()


@router.post("/curiosity", response_model=CuriosityResponse)
async def curiosity_suggestions(req: CuriosityRequest):
    if not req.page_content.strip():
        raise HTTPException(status_code=400, detail="Page content is empty")

    settings = get_settings()
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
