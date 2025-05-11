from pathlib import Path

from pydantic import Field
from typing import Optional, Any, Dict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_file_encoding="utf-8",
    )

    # Azure OpenAI configuration
    AZURE_API_KEY: str
    AZURE_BASE_URL: str
    AZURE_API_VERSION: str
    AZURE_MODEL_NAME: str

    # MongoDB configuration
    MONGO_URI: str = Field(
        description="Connection URI for the MongoDB Atlas instance"
    )
    DB_NAME: str
    STATE_CHECKPOINT_COLLECTION: str
    STATE_WRITES_COLLECTION: str
    LONG_TERM_MEMORY_COLLECTION: str
    LONG_TERM_MEMORY_SEARCH_INDEX_NAME: str
    COSMETIC_SURGEON_COLLECTION: str
    COSMETIC_SURGEON_SEARCH_INDEX_NAME: str
    COSMETIC_SURGEON_VECTOR_STORE: str

    # RAG configuration
    TEXT_EMBEDDING_MODEL_ID: str
    TOTAL_MESSAGES_SUMMARY_TRIGGER: int
    TOTAL_MESSAGES_AFTER_SUMMARY: int
    CHUNK_SIZE: int
    TOP_K: int
    DEVICE: str

    # Comet configuration
    COMET_API_KEY: str
    COMET_WORKSPACE: str
    COMET_PROJECT: str


settings = Settings()