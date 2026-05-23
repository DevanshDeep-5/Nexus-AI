"""
POST /highlight-action — Highlight-Based Text Actions Endpoint
-----------------------------------------------------------------
Processes an action on text that the user selected/highlighted on the page.
Supports four actions: explain, simplify, summarize, and examples.
These are triggered from the floating action menu in the content script.
"""

from fastapi import APIRouter, HTTPException
from app.schemas import HighlightActionRequest, HighlightActionResponse
from app.services.llm import call_llm, HIGHLIGHT_PROMPTS

router = APIRouter()


@router.post("/highlight-action", response_model=HighlightActionResponse)
async def highlight_action(req: HighlightActionRequest):
    """Process a highlight-based action (explain, simplify, summarize, examples)."""

    if not req.selected_text.strip():
        raise HTTPException(status_code=400, detail="Selected text is empty")

    # Validate the action type against our supported actions
    action = req.action.lower()
    if action not in HIGHLIGHT_PROMPTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action. Must be one of: {', '.join(HIGHLIGHT_PROMPTS.keys())}",
        )

    try:
        # Build the prompt, limiting page context to 2000 chars to save tokens
        prompt = HIGHLIGHT_PROMPTS[action].format(
            text=req.selected_text,
            context=req.page_context[:2000] if req.page_context else "No additional context.",
        )

        # Highlight actions return plain text, not JSON
        result = await call_llm(prompt, json_mode=False)

        return HighlightActionResponse(result=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
