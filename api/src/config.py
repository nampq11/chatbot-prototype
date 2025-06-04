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
    DB_NAME: str = "bookingcare"
    STATE_CHECKPOINT_COLLECTION: str = "state_checkpoint"
    STATE_WRITES_COLLECTION: str = "state_writes"
    LONG_TERM_MEMORY_COLLECTION: str = "long_term_memory"
    LONG_TERM_MEMORY_SEARCH_INDEX_NAME: str = "long_term_memory_search_index"
    COSMETIC_SURGEON_COLLECTION: str = "cosmetic_surgeon"
    COSMETIC_SURGEON_SEARCH_INDEX_NAME: str = "cosmetic_surgeon_search_index"
    COSMETIC_SURGEON_VECTOR_STORE: str = "cosmetic_surgeon_vector_store"

    # RAG configuration
    TEXT_EMBEDDING_MODEL_ID: str = "BookingCare/gte-multilingual-base-v2.1"
    TOTAL_MESSAGES_SUMMARY_TRIGGER: int = 30
    TOTAL_MESSAGES_AFTER_SUMMARY: int = 5
    CHUNK_SIZE: int = 256
    TOP_K: int = 3
    DEVICE: str = "cpu"

    # Comet configuration
    COMET_API_KEY: str
    COMET_WORKSPACE: str
    COMET_PROJECT: str


settings = Settings()