"""
LLM Client & Prompt Templates
-------------------------------
This module handles all communication with the AI language model.
It provides:
  1. A singleton OpenAI-compatible client (works with OpenRouter, Gemini, or OpenAI)
  2. Prompt templates for every AI feature (summarize, notes, debate, etc.)
  3. Helper functions to call the LLM and parse JSON responses
"""

import json

from openai import APIStatusError, AsyncOpenAI

from app.config import get_settings


def _format_api_error(exc: APIStatusError) -> str:
    """Turn API HTTP errors into a short user-facing message."""
    message = str(exc.message) if exc.message else str(exc)
    try:
        body = exc.body
        if isinstance(body, dict):
            err = body.get("error") or {}
            if isinstance(err, dict) and err.get("message"):
                return str(err["message"])
    except Exception:
        pass
    if "402" in message or "Insufficient credits" in message:
        return (
            "The AI provider has no credits / quota for this model. "
            "Check your API key and model settings in backend/.env."
        )
    if "429" in message:
        return "Model rate-limited. Wait a moment and try again, or switch OPENAI_MODEL in .env."
    if "401" in message or "unauthorized" in message.lower():
        return (
            "Authentication failed. Check your OPENAI_API_KEY in backend/.env "
            "and ensure the token has the required permissions."
        )
    return message

# ── Singleton LLM Client ───────────────────────────────────────────
# We reuse one client instance across all requests to avoid
# recreating HTTP connections on every API call.

_client: AsyncOpenAI | None = None


def reset_client() -> None:
    """Force the singleton client to be recreated on next use. Call this when settings change."""
    global _client
    _client = None


def get_client() -> AsyncOpenAI:
    """
    Returns a singleton AsyncOpenAI client configured for the correct provider.

    The provider is auto-detected from the API key prefix:
      - "sk-or-v1-..." → OpenRouter (proxy to many models)
      - "AIzaSy..."    → Google Gemini (OpenAI-compatible endpoint)
      - "github_pat_"  → GitHub Models (OpenAI-compatible endpoint)
      - anything else  → Standard OpenAI API
    """
    global _client
    if _client is not None:
        return _client

    settings = get_settings()

    base_url = None
    if settings.openai_api_key.startswith("sk-or-v1-"):
        base_url = "https://openrouter.ai/api/v1"
    elif settings.openai_api_key.startswith("AIzaSy"):
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
    elif settings.openai_api_key.startswith("github_pat_"):
        base_url = "https://models.inference.ai.azure.com"

    _client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=base_url,
        timeout=90.0,   # Increased: large pages (e.g. Wikipedia) need more time
        max_retries=1,
    )
    return _client


# ── Prompt Templates ───────────────────────────────────────────────
# Each template is a string with {placeholders} that get filled in
# by the route handlers before being sent to the LLM.

# System prompt — tells the AI to only answer from the given content
SYSTEM_GROUNDED = """You are a helpful AI assistant that answers questions ONLY based on the provided webpage content.

STRICT RULES:
1. Answer ONLY from the provided content. Do NOT use external knowledge.
2. If the answer is not found in the content, respond EXACTLY: "Not mentioned in the page."
3. When answering, include the exact relevant quote(s) from the content as sources.
4. Be concise but thorough.
5. Format your answer in clean markdown."""

# Q&A prompt — used by the /ask endpoint for RAG-powered answers
ASK_PROMPT = """Based on the following webpage content, answer the user's question.

WEBPAGE CONTENT (relevant excerpts):
{context}

USER QUESTION: {question}

Respond in JSON format:
{{
  "answer": "your answer here (markdown formatted)",
  "sources": ["exact quote 1 used as source", "exact quote 2 used as source"]
}}"""

# Summary prompt — used by the /summarize endpoint
SUMMARIZE_PROMPT = """Analyze the following webpage content and provide a structured TL;DR summary.

WEBPAGE CONTENT:
{content}

Respond in JSON format:
{{
  "key_points": ["point 1", "point 2", "point 3", "point 4", "point 5"],
  "insights": ["insight 1", "insight 2", "insight 3"],
  "takeaway": "one-sentence final takeaway"
}}"""

# ELI5 prompt — used by the /eli5 endpoint for simplified explanations
ELI5_PROMPT = """Explain the following webpage content as if explaining to a 5-year-old child.

Use:
- Simple words
- Fun analogies
- Short sentences
- Relatable examples

WEBPAGE CONTENT:
{content}

Respond in JSON format:
{{
  "explanation": "your ELI5 explanation here"
}}"""

# Keypoints prompt — used by the /keypoints endpoint
KEYPOINTS_PROMPT = """Extract the most important key points from this webpage content.

WEBPAGE CONTENT:
{content}

Respond in JSON format:
{{
  "keypoints": ["key point 1", "key point 2", "key point 3", ...]
}}"""

# Debate prompt — used by the /debate endpoint for balanced analysis
DEBATE_PROMPT = """Analyze the following webpage content and present a balanced debate.

Show arguments that SUPPORT the content's claims/perspective, and arguments AGAINST or that challenge it.

WEBPAGE CONTENT:
{content}

Respond in JSON format:
{{
  "arguments_for": ["supporting argument 1", "supporting argument 2", "supporting argument 3"],
  "arguments_against": ["counter argument 1", "counter argument 2", "counter argument 3"],
  "verdict": "balanced one-sentence conclusion"
}}"""

# Notes prompt — used by the /notes endpoint for structured study notes
NOTES_PROMPT = """Convert the following webpage content into well-structured study notes.

Include:
- A descriptive title
- Organized sections with clear headings
- Bullet points for key information
- Key terms/vocabulary highlighted

WEBPAGE CONTENT:
{content}

Respond in JSON format:
{{
  "title": "Notes title",
  "sections": [
    {{
      "heading": "Section heading",
      "bullets": ["bullet 1", "bullet 2"],
      "key_terms": ["term 1", "term 2"]
    }}
  ]
}}"""

# Curiosity prompt — used by the /curiosity endpoint for follow-up questions
CURIOSITY_PROMPT = """Based on the following webpage content, generate insightful follow-up questions that a curious reader might want to explore.

Include questions like:
- "What evidence supports this?"
- "Are there counterarguments?"
- "What are the implications?"
- "How does this compare to...?"

WEBPAGE CONTENT:
{content}

Respond in JSON format:
{{
  "questions": ["question 1", "question 2", "question 3", "question 4", "question 5"]
}}"""

# Highlight action prompts — used when user selects text on a page
# Each key maps to a different action the user can take on highlighted text
HIGHLIGHT_PROMPTS = {
    "explain": "Explain the following text clearly and in detail:\n\n\"{text}\"\n\nContext from the page:\n{context}",
    "simplify": "Simplify the following text so anyone can understand it. Use plain language:\n\n\"{text}\"\n\nContext from the page:\n{context}",
    "summarize": "Provide a brief summary of the following text:\n\n\"{text}\"\n\nContext from the page:\n{context}",
    "examples": "Give practical, real-world examples that illustrate the concept in the following text:\n\n\"{text}\"\n\nContext from the page:\n{context}",
}


# ── LLM Call Functions ─────────────────────────────────────────────

async def call_llm(
    prompt: str,
    system: str = SYSTEM_GROUNDED,
    json_mode: bool = True,
) -> str:
    """
    Send a prompt to the LLM and return the raw response text.
    Handles dynamic fallbacks for rate limits and format errors.
    """
    settings = get_settings()
    client = get_client()

    # Pre-populate candidate models list to dynamically recover from rate limiting
    original_model = settings.openai_model
    models_to_try = [original_model]
    
    # If the user is on OpenRouter free tier, add highly reliable fallback free models
    if settings.openai_api_key.startswith("sk-or-v1-"):
        fallbacks = [
            "openrouter/free",
            "google/gemma-4-26b-a4b-it:free",
            "google/gemma-4-31b-it:free",
            "meta-llama/llama-3.2-3b-instruct:free",
            "meta-llama/llama-3.3-70b-instruct:free",
        ]
        for fb in fallbacks:
            if fb not in models_to_try:
                models_to_try.append(fb)

    # GitHub Models: gpt-4o-mini is the primary; fall back to gpt-4o if needed
    if settings.openai_api_key.startswith("github_pat_"):
        fallbacks = ["gpt-4o-mini", "gpt-4o"]
        for fb in fallbacks:
            if fb not in models_to_try:
                models_to_try.append(fb)

    last_exc = None
    
    # Attempt candidate models in sequence
    for model_name in models_to_try:
        kwargs = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 2048,
        }

        # Try with JSON format first if requested
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = await client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
        except APIStatusError as exc:
            status_code = getattr(exc, "status_code", 0)

            # If json_mode is True and the model does not support it (400, 404, 422),
            # gracefully fall back to requesting normal text output.
            if json_mode and status_code in (400, 404, 422):
                try:
                    kwargs_no_json = kwargs.copy()
                    kwargs_no_json.pop("response_format", None)
                    kwargs_no_json["messages"].append({
                        "role": "user",
                        "content": "CRITICAL: Respond ONLY with a valid, clean JSON object. Do not include markdown formatting like ```json."
                    })
                    response = await client.chat.completions.create(**kwargs_no_json)
                    return response.choices[0].message.content or ""
                except APIStatusError as inner_exc:
                    exc = inner_exc
                    status_code = getattr(inner_exc, "status_code", 0)

            # For transient provider rate limits (429) or quota errors (402) or server downtime, try fallback models
            if status_code in (429, 402, 500, 502, 503, 504):
                last_exc = exc
                continue

            raise RuntimeError(_format_api_error(exc)) from exc

    if last_exc:
        raise RuntimeError(_format_api_error(last_exc)) from last_exc
    raise RuntimeError("All configured fallback models failed.")


def as_list(value) -> list:
    """
    Coerce LLM JSON fields into a list.

    `.get("key", [])` still returns None when the model sends `"key": null`.
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def extract_and_parse_json(text: str) -> dict:
    """Extracts and parses JSON from raw LLM text even if wrapped in markdown code blocks."""
    text = text.strip()
    
    # 1. Clean JSON parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    # 2. Check for markdown code block (```json ... ```)
    if "```json" in text:
        try:
            start = text.index("```json") + 7
            end = text.index("```", start)
            return json.loads(text[start:end].strip())
        except Exception:
            pass
            
    # 3. Check for generic code block (``` ... ```)
    if "```" in text:
        try:
            start = text.index("```") + 3
            end = text.index("```", start)
            return json.loads(text[start:end].strip())
        except Exception:
            pass
            
    # 4. Extract first matching brace set {...}
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except Exception:
        pass
        
    return {"error": "Failed to parse AI response as JSON", "raw": text}


async def call_llm_json(prompt: str, system: str = SYSTEM_GROUNDED) -> dict:
    """
    Send a prompt to the LLM and parse the response as JSON.
    Recursively recovers if json_mode fails.
    """
    try:
        raw = await call_llm(prompt, system, json_mode=True)
    except Exception:
        # Fallback to normal text-mode if json_mode completely crashed
        try:
            raw = await call_llm(prompt, system, json_mode=False)
        except Exception as e:
            return {"error": str(e)}

    return extract_and_parse_json(raw)
