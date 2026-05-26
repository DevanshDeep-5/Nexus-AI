from fastapi import APIRouter, HTTPException
from app.schemas import KeypointsRequest, KeypointsResponse
from app.services.llm import call_llm_json, KEYPOINTS_PROMPT, as_list
from app.services.text_processor import clean_text, truncate_text
from app.config import get_settings

router = APIRouter()


@router.post("/keypoints", response_model=KeypointsResponse)
async def extract_keypoints(req: KeypointsRequest):
    if not req.page_content.strip():
        raise HTTPException(status_code=400, detail="Page content is empty")

    settings = get_settings()
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
