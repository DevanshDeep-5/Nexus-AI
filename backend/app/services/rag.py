import asyncio
import os
import uuid

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb
from chromadb.utils import embedding_functions

from app.config import get_settings
from app.services.text_processor import TextChunk, chunk_text, clean_text, truncate_text
from app.services.llm import get_client

_local_embed_fn = None


def _use_local_embeddings() -> bool:
    key = get_settings().openai_api_key
    return key.startswith("sk-or-v1-") or key.startswith("github_pat_")


def _embed_locally(texts: list[str]) -> list[list[float]]:
    global _local_embed_fn
    if _local_embed_fn is None:
        _local_embed_fn = embedding_functions.DefaultEmbeddingFunction()
    return _local_embed_fn(texts)


async def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Get embeddings - uses local if on OpenRouter/GitHub, otherwise OpenAI API."""
    if _use_local_embeddings():
        return await asyncio.to_thread(_embed_locally, texts)

    settings = get_settings()
    client = get_client()

    response = await client.embeddings.create(
        model=settings.openai_embedding_model,
        input=texts,
    )
    return [item.embedding for item in response.data]


async def retrieve_relevant_chunks(query: str, page_content: str, top_k: int | None = None) -> list[TextChunk]:
    """Find the most relevant chunks for a query using vector search."""
    settings = get_settings()
    if top_k is None:
        top_k = settings.top_k_results

    content = clean_text(page_content)
    content = truncate_text(content, settings.max_page_length)

    chunks = chunk_text(content, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        return []

    # If we have fewer chunks than top_k, just return all of them
    if len(chunks) <= top_k:
        return chunks

    chroma = chromadb.Client(chromadb.Settings(anonymized_telemetry=False))
    collection_name = f"page_chunks_{uuid.uuid4().hex}"

    try:
        collection = chroma.create_collection(
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
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

        relevant_chunks = []
        docs = (results or {}).get("documents") or []
        metas = (results or {}).get("metadatas") or []
        doc_list = docs[0] if docs and docs[0] else []
        meta_list = metas[0] if metas and metas[0] else []

        for i, doc in enumerate(doc_list):
            meta = meta_list[i] if i < len(meta_list) and meta_list[i] else {}
            relevant_chunks.append(TextChunk(
                text=doc,
                index=meta.get("index", i),
                start_char=meta.get("start", 0),
                end_char=meta.get("end", 0),
            ))

        return relevant_chunks
    finally:
        try:
            chroma.delete_collection(collection_name)
        except Exception:
            pass


def format_context(chunks: list[TextChunk]) -> str:
    """Format chunks into a numbered context string for the LLM."""
    if not chunks:
        return "No relevant content found."

    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[Excerpt {i}]:\n{chunk.text}")
    return "\n\n".join(parts)
