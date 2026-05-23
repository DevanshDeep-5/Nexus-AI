"""
RAG (Retrieval-Augmented Generation) Pipeline
-----------------------------------------------
This module implements the core RAG flow used by the /ask endpoint:

  1. Clean & truncate the raw page content
  2. Split it into overlapping text chunks
  3. Generate vector embeddings for each chunk
  4. Store embeddings in an ephemeral ChromaDB collection
  5. Embed the user's question and find the most relevant chunks
  6. Return those chunks so they can be injected into the LLM prompt

This approach ensures the AI only sees the most relevant parts of the page,
which produces more accurate answers and reduces token usage.
"""

import asyncio
import os
import uuid

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb
from chromadb.utils import embedding_functions

from app.config import get_settings
from app.services.text_processor import TextChunk, chunk_text, clean_text, truncate_text
from app.services.llm import get_client

_local_embedding_fn = None


def _uses_local_embeddings() -> bool:
    key = get_settings().openai_api_key
    return key.startswith("sk-or-v1-") or key.startswith("github_pat_")


def _embed_locally(texts: list[str]) -> list[list[float]]:
    """Free on-device embeddings (no OpenRouter credits)."""
    global _local_embedding_fn
    if _local_embedding_fn is None:
        _local_embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    return _local_embedding_fn(texts)


# ── Embedding Generation ───────────────────────────────────────────

async def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate vector embeddings for a list of text strings.

    OpenRouter keys use local Chroma embeddings (free). Direct OpenAI keys
    use the paid embeddings API configured in OPENAI_EMBEDDING_MODEL.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors (one per input text).
    """
    if _uses_local_embeddings():
        return await asyncio.to_thread(_embed_locally, texts)

    settings = get_settings()
    client = get_client()

    response = await client.embeddings.create(
        model=settings.openai_embedding_model,
        input=texts,
    )
    return [item.embedding for item in response.data]


# ── Main Retrieval Pipeline ────────────────────────────────────────

async def retrieve_relevant_chunks(
    query: str,
    page_content: str,
    top_k: int | None = None,
) -> list[TextChunk]:
    """
    Full RAG retrieval pipeline: finds the most relevant chunks for a query.

    Steps:
      1. Clean and truncate the page content
      2. Split into overlapping chunks
      3. Embed all chunks + the query
      4. Use ChromaDB to find the top-k most similar chunks

    Args:
        query:        The user's question.
        page_content: Raw text extracted from the webpage.
        top_k:        Number of chunks to retrieve (defaults to config value).

    Returns:
        List of the most relevant TextChunk objects.
    """
    settings = get_settings()
    if top_k is None:
        top_k = settings.top_k_results

    cleaned = clean_text(page_content)
    cleaned = truncate_text(cleaned, settings.max_page_length)

    chunks = chunk_text(cleaned, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        return []

    if len(chunks) <= top_k:
        return chunks

    chroma_client = chromadb.Client(chromadb.Settings(anonymized_telemetry=False))
    collection_name = f"page_chunks_{uuid.uuid4().hex}"

    try:
        collection = chroma_client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        chunk_texts = [c.text for c in chunks]
        chunk_embeddings = await get_embeddings(chunk_texts)

        collection.add(
            ids=[f"chunk_{i}" for i in range(len(chunks))],
            embeddings=chunk_embeddings,
            documents=chunk_texts,
            metadatas=[
                {"index": c.index, "start": c.start_char, "end": c.end_char}
                for c in chunks
            ],
        )

        query_embedding = (await get_embeddings([query]))[0]

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        relevant_chunks = []
        docs = (results or {}).get("documents") or []
        metas = (results or {}).get("metadatas") or []
        doc_list = docs[0] if docs and docs[0] else []
        meta_list = metas[0] if metas and metas[0] else []

        for i, doc in enumerate(doc_list):
            meta = meta_list[i] if i < len(meta_list) and meta_list[i] else {}
            relevant_chunks.append(
                TextChunk(
                    text=doc,
                    index=meta.get("index", i),
                    start_char=meta.get("start", 0),
                    end_char=meta.get("end", 0),
                )
            )

        return relevant_chunks
    finally:
        try:
            chroma_client.delete_collection(collection_name)
        except Exception:
            pass


# ── Context Formatting ─────────────────────────────────────────────

def format_context(chunks: list[TextChunk]) -> str:
    """
    Format retrieved chunks into a readable context string for the LLM prompt.

    Each chunk is numbered as an "Excerpt" so the LLM can reference them
    when citing sources in its answer.

    Args:
        chunks: List of TextChunk objects from the retrieval step.

    Returns:
        A formatted string with numbered excerpts, or a fallback message.
    """
    if not chunks:
        return "No relevant content found."

    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[Excerpt {i}]:\n{chunk.text}")
    return "\n\n".join(parts)
