#!/usr/bin/env python3
"""Quick smoke test for the Ask This Page AI backend."""

import asyncio
import sys

import httpx

BASE = "http://127.0.0.1:8000"
SAMPLE_PAGE = """
Ask This Page AI is a Chrome extension that lets users ask questions about webpages.
It uses a FastAPI backend with RAG retrieval and an LLM to answer from page content only.
Features include summarize, notes, debate mode, and YouTube transcript support.
""".strip()


async def main() -> int:
    async with httpx.AsyncClient(timeout=180.0) as client:
        health = await client.get(f"{BASE}/health")
        print(f"GET /health -> {health.status_code} {health.json()}")
        if health.status_code != 200:
            return 1

        payload = {
            "question": "What is Ask This Page AI?",
            "page_content": SAMPLE_PAGE,
            "page_url": "https://example.com/test",
        }

        for endpoint in ("/curiosity", "/summarize", "/ask"):
            print(f"\nPOST {endpoint} ...")
            res = await client.post(f"{BASE}{endpoint}", json=payload if endpoint == "/ask" else {
                "page_content": payload["page_content"],
                "page_url": payload["page_url"],
            })
            print(f"  status: {res.status_code}")
            if res.status_code != 200:
                print(f"  error: {res.text[:500]}")
                return 1
            body = res.json()
            if endpoint == "/ask":
                print(f"  answer: {body.get('answer', '')[:120]}...")
            elif endpoint == "/curiosity":
                print(f"  questions: {body.get('questions', [])[:2]}")
            else:
                print(f"  keys: {list(body.keys())}")

    print("\nAll smoke tests passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except httpx.ConnectError:
        print("Cannot connect to backend. Start: uvicorn main:app --reload --port 8000", file=sys.stderr)
        raise SystemExit(1)
