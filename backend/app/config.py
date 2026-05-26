from functools import lru_cache
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API keys
    openai_api_key: str = ""
    openrouter_api_key: str = ""

    # Model config
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    # Text chunking settings for RAG
    chunk_size: int = 512
    chunk_overlap: int = 50
    max_page_length: int = 100_000
    top_k_results: int = 5

    @model_validator(mode="after")
    def resolve_api_key(self) -> Self:
        # Use openrouter key as fallback if openai key not set
        openai_key = self.openai_api_key.strip().strip("'\"")
        openrouter_key = self.openrouter_api_key.strip().strip("'\"")

        if openai_key:
            self.openai_api_key = openai_key
        elif openrouter_key:
            self.openai_api_key = openrouter_key
        else:
            self.openai_api_key = ""

        self.openrouter_api_key = openrouter_key
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
