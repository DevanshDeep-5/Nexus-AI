import os

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import ask, summarize, eli5, keypoints, debate, notes, curiosity, youtube, highlight

app = FastAPI(title="Ask This Page AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ask.router, tags=["Q&A"])
app.include_router(summarize.router, tags=["Summary"])
app.include_router(eli5.router, tags=["ELI5"])
app.include_router(keypoints.router, tags=["Keypoints"])
app.include_router(debate.router, tags=["Debate"])
app.include_router(notes.router, tags=["Notes"])
app.include_router(curiosity.router, tags=["Curiosity"])
app.include_router(youtube.router, tags=["YouTube"])
app.include_router(highlight.router, tags=["Highlight Actions"])


@app.get("/")
async def root():
    return {"name": "Ask This Page AI", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
