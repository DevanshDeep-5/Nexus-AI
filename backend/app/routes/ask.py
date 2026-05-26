from fastapi import APIRouter, HTTPException
from app.schemas import AskRequest, AskResponse, SourceExcerpt
from app.services.rag import retrieve_relevant_chunks, format_context
from app.services.llm import call_llm_json, ASK_PROMPT, as_list

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
async def ask_question(req: AskRequest):
    if not req.page_content.strip():
        raise HTTPException(status_code=400, detail="Page content is empty")
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question is empty")

    try:
        chunks = await retrieve_relevant_chunks(req.question, req.page_content)
        context = format_context(chunks)

        prompt = ASK_PROMPT.format(context=context, question=req.question)
        data = await call_llm_json(prompt)

        if data.get("error") and not data.get("answer"):
            raise HTTPException(status_code=502, detail=str(data.get("error")))

        answer = (data.get("answer") or "").strip()
        if not answer:
            raise HTTPException(
                status_code=502,
                detail="The AI returned an empty answer. Try rephrasing your question.",
            )

        return AskResponse(
            answer=answer,
            sources=[
                SourceExcerpt(text=str(s), relevance=0.9)
                for s in as_list(data.get("sources"))
                if s
            ],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
