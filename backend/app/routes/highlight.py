from fastapi import APIRouter, HTTPException
from app.schemas import HighlightActionRequest, HighlightActionResponse
from app.services.llm import call_llm, HIGHLIGHT_PROMPTS

router = APIRouter()


@router.post("/highlight-action", response_model=HighlightActionResponse)
async def highlight_action(req: HighlightActionRequest):
    if not req.selected_text.strip():
        raise HTTPException(status_code=400, detail="Selected text is empty")

    action = req.action.lower()
    if action not in HIGHLIGHT_PROMPTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action. Must be one of: {', '.join(HIGHLIGHT_PROMPTS.keys())}",
        )

    try:
        context = req.page_context[:2000] if req.page_context else "No additional context."
        prompt = HIGHLIGHT_PROMPTS[action].format(text=req.selected_text, context=context)
        result = await call_llm(prompt, json_mode=False)

        return HighlightActionResponse(result=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
