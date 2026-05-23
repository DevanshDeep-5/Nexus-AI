"""
POST /ask — RAG-Powered Q&A Endpoint
--------------------------------------
Accepts a user question and the page content, retrieves the most relevant
chunks via the RAG pipeline, then asks the LLM to answer using only those
chunks as context. Returns the answer along with source excerpts.
"""

from fastapi import APIRouter, HTTPException
from app.schemas import AskRequest, AskResponse, SourceExcerpt
from app.services.rag import retrieve_relevant_chunks, format_context
from app.services.llm import call_llm_json, ASK_PROMPT, as_list

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
async def ask_question(req: AskRequest):
    """Answer a question using RAG retrieval over the page content."""

    # Validate that we have content and a question to work with
    if not req.page_content.strip():
        raise HTTPException(status_code=400, detail="Page content is empty")
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question is empty")

    try:
        # Step 1: Retrieve the most relevant chunks from the page
        chunks = await retrieve_relevant_chunks(req.question, req.page_content)
        context = format_context(chunks)

        # Step 2: Ask the LLM to answer using only the retrieved context
        prompt = ASK_PROMPT.format(context=context, question=req.question)
        data = await call_llm_json(prompt)

        # Surface JSON-parse failures or hard provider errors
        if data.get("error") and not data.get("answer"):
            raise HTTPException(status_code=502, detail=str(data.get("error")))

        # "answer" can be "Not mentioned in the page." — that is a valid response
        answer = (data.get("answer") or "").strip()
        if not answer:
            # The model returned JSON but no answer field at all — something is wrong
            raise HTTPException(
                status_code=502,
                detail="The AI returned an empty answer. Try again or rephrase your question.",
            )

        # Step 3: Build and return the structured response
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

