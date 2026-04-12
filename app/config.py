from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = Field(default="")
    chat_model: str = Field(default="gpt-4.1-mini")
    embedding_model: str = Field(default="text-embedding-3-large")

    chroma_persist_directory: Path = Field(default=Path("./data/chroma"))
    collection_prefix: str = Field(default="rag")

    chunk_size: int = Field(default=1000, ge=200, le=4000)
    chunk_overlap: int = Field(default=150, ge=0, le=1000)
    top_k: int = Field(default=6, ge=1, le=20)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

