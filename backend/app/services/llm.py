import json

from openai import APIStatusError, AsyncOpenAI
from app.config import get_settings


def _get_error_message(exc: APIStatusError) -> str:
    """Convert API errors into something readable."""
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
        return "No credits left for this model. Check your API key in backend/.env."
    if "429" in message:
        return "Rate limited. Wait a bit then try again."
    if "401" in message or "unauthorized" in message.lower():
        return "Invalid API key. Check OPENAI_API_KEY in backend/.env."
    return message


# Singleton client - we only want to create this once
_client: AsyncOpenAI | None = None


def reset_client() -> None:
    global _client
    _client = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is not None:
        return _client

    settings = get_settings()
    key = settings.openai_api_key

    base_url = None
    if key.startswith("sk-or-v1-"):
        base_url = "https://openrouter.ai/api/v1"
    elif key.startswith("AIzaSy"):
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
    elif key.startswith("github_pat_"):
        base_url = "https://models.inference.ai.azure.com"

    _client = AsyncOpenAI(
        api_key=key,
        base_url=base_url,
        timeout=90.0,
        max_retries=1,
    )
    return _client


# ---- Prompt Templates ----

SYSTEM_GROUNDED = """You are a helpful AI assistant that answers questions ONLY based on the provided webpage content.

STRICT RULES:
1. Answer ONLY from the provided content. Do NOT use external knowledge.
2. If the answer is not found in the content, respond EXACTLY: "Not mentioned in the page."
3. When answering, include the exact relevant quote(s) from the content as sources.
4. Be concise but thorough.
5. Format your answer in clean markdown."""

ASK_PROMPT = """Based on the following webpage content, answer the user's question.

WEBPAGE CONTENT (relevant excerpts):
{context}

USER QUESTION: {question}

Respond in JSON format:
{{
  "answer": "your answer here (markdown formatted)",
  "sources": ["exact quote 1 used as source", "exact quote 2 used as source"]
}}"""

SUMMARIZE_PROMPT = """Analyze the following webpage content and provide a structured TL;DR summary.

WEBPAGE CONTENT:
{content}

Respond in JSON format:
{{
  "key_points": ["point 1", "point 2", "point 3", "point 4", "point 5"],
  "insights": ["insight 1", "insight 2", "insight 3"],
  "takeaway": "one-sentence final takeaway"
}}"""

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

KEYPOINTS_PROMPT = """Extract the most important key points from this webpage content.

WEBPAGE CONTENT:
{content}

Respond in JSON format:
{{
  "keypoints": ["key point 1", "key point 2", "key point 3", ...]
}}"""

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

HIGHLIGHT_PROMPTS = {
    "explain": "Explain the following text clearly and in detail:\n\n\"{text}\"\n\nContext from the page:\n{context}",
    "simplify": "Simplify the following text so anyone can understand it. Use plain language:\n\n\"{text}\"\n\nContext from the page:\n{context}",
    "summarize": "Provide a brief summary of the following text:\n\n\"{text}\"\n\nContext from the page:\n{context}",
    "examples": "Give practical, real-world examples that illustrate the concept in the following text:\n\n\"{text}\"\n\nContext from the page:\n{context}",
}


# ---- LLM Call Helpers ----

async def call_llm(prompt: str, system: str = SYSTEM_GROUNDED, json_mode: bool = True) -> str:
    settings = get_settings()
    client = get_client()

    model = settings.openai_model
    models_to_try = [model]

    # Add fallback models for OpenRouter free tier
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

    # GitHub Models fallbacks
    if settings.openai_api_key.startswith("github_pat_"):
        for fb in ["gpt-4o-mini", "gpt-4o"]:
            if fb not in models_to_try:
                models_to_try.append(fb)

    last_error = None

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

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = await client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
        except APIStatusError as exc:
            status_code = getattr(exc, "status_code", 0)

            # Some models don't support json_mode, try without it
            if json_mode and status_code in (400, 404, 422):
                try:
                    fallback_kwargs = kwargs.copy()
                    fallback_kwargs.pop("response_format", None)
                    fallback_kwargs["messages"].append({
                        "role": "user",
                        "content": "CRITICAL: Respond ONLY with a valid, clean JSON object. Do not include markdown formatting like ```json."
                    })
                    response = await client.chat.completions.create(**fallback_kwargs)
                    return response.choices[0].message.content or ""
                except APIStatusError as inner_exc:
                    exc = inner_exc
                    status_code = getattr(inner_exc, "status_code", 0)

            # Retry with next model on rate limit or server errors
            if status_code in (429, 402, 500, 502, 503, 504):
                last_error = exc
                continue

            raise RuntimeError(_get_error_message(exc)) from exc

    if last_error:
        raise RuntimeError(_get_error_message(last_error)) from last_error
    raise RuntimeError("All configured fallback models failed.")


def as_list(value) -> list:
    """Make sure we always get a list even if the LLM returns null."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def extract_and_parse_json(text: str) -> dict:
    """Try to parse JSON from LLM response, handling markdown code blocks."""
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Handle ```json ... ``` blocks
    if "```json" in text:
        try:
            start = text.index("```json") + 7
            end = text.index("```", start)
            return json.loads(text[start:end].strip())
        except Exception:
            pass

    # Handle generic ``` ... ``` blocks
    if "```" in text:
        try:
            start = text.index("```") + 3
            end = text.index("```", start)
            return json.loads(text[start:end].strip())
        except Exception:
            pass

    # Last resort: find the first { ... } pair
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except Exception:
        pass

    return {"error": "Failed to parse AI response as JSON", "raw": text}


async def call_llm_json(prompt: str, system: str = SYSTEM_GROUNDED) -> dict:
    """Call LLM and parse the JSON response."""
    try:
        raw = await call_llm(prompt, system, json_mode=True)
    except Exception:
        try:
            raw = await call_llm(prompt, system, json_mode=False)
        except Exception as e:
            return {"error": str(e)}

    return extract_and_parse_json(raw)
