"""
Application Settings Module
----------------------------
Loads configuration from environment variables (or a .env file) using
Pydantic Settings. This gives us type-safe access to all config values
throughout the application, with sensible defaults as fallbacks.
"""

from functools import lru_cache
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings


def _strip_env_value(value: str) -> str:
    """Remove surrounding quotes/whitespace from .env values."""
    return value.strip().strip("'\"")


class Settings(BaseSettings):
    """
    Centralized configuration for the Ask This Page AI backend.

    Each field maps directly to an environment variable (case-insensitive).
    For example, `openai_api_key` reads from `OPENAI_API_KEY` in the .env file.
    """

    # ── LLM Provider ────────────────────────────────────────────────
    # API key for the LLM provider (OpenRouter, OpenAI, or Google Gemini)
    openai_api_key: str = ""

    # Optional alias — some setups use OPENROUTER_API_KEY instead
    openrouter_api_key: str = ""

    # Model identifier — format depends on the provider:
    #   OpenAI:     "gpt-4o"
    #   OpenRouter: "google/gemini-2.0-flash-lite-001"
    #   Gemini:     "gemini-2.0-flash"
    openai_model: str = "gpt-4o"

    # Embedding model used by the RAG pipeline for vector similarity search
    openai_embedding_model: str = "text-embedding-3-small"

    # ── Text Processing ─────────────────────────────────────────────
    # Number of characters per text chunk when splitting page content
    chunk_size: int = 512

    # Character overlap between adjacent chunks to preserve context
    chunk_overlap: int = 50

    # Maximum page content length (in characters) sent to the LLM.
    # Prevents exceeding the provider's token limits.
    max_page_length: int = 100_000

    # Number of top-matching chunks returned by the RAG retriever
    top_k_results: int = 5

    @model_validator(mode="after")
    def resolve_api_key(self) -> Self:
        """Use OPENROUTER_API_KEY when OPENAI_API_KEY is not set."""
        openai = _strip_env_value(self.openai_api_key)
        openrouter = _strip_env_value(self.openrouter_api_key)
        if openai:
            self.openai_api_key = openai
        elif openrouter:
            self.openai_api_key = openrouter
        else:
            self.openai_api_key = ""
        self.openrouter_api_key = openrouter
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached singleton of the application settings.

    Using @lru_cache ensures the .env file is read only once,
    and the same Settings object is reused across all requests.
    """
    return Settings()
