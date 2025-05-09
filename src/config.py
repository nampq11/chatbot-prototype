from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
import streamlit as st

class InputArgs(BaseModel):
    """Input arguments for API configuration."""
    AZURE_API_KEY: str
    AZURE_BASE_URL: str
    AZURE_API_VERSION: str
    openai_api_key: str 
    gemini_api_key: str

class MongoConfig(BaseModel):
    """MongoDB configuration settings."""
    URI: str = Field(
        default=st.secrets.mongodb_credential.get("MONGO_URI", ""),
        description="MongoDB connection URI"
    )
    DB_NAME: str = Field(
        default="healthcare",
        description="MongoDB database name"
    )
    STATE_CHECKPOINT_COLLECTION: str = Field(
        default="healthcare_state_checkpoints",
        description="Collection for state checkpoints"
    )
    STATE_WRITES_COLLECTION: str = Field(
        default="healthcare_state_writes",
        description="Collection for state writes"
    )
    LONG_TERM_MEMORY_COLLECTION: str = Field(
        default="healthcare_long_term_memory",
        description="Collection for long term memory"
    )
    LONG_TERM_MEMORY_SEARCH_INDEX_NAME: str = Field(
        default="healthcare_long_term_memory_search_index",
        description="Search index name for long term memory"
    )
    COSMETIC_SURGEON_COLLECTION: str = Field(
        default="Cosmetic_surgeon",
        description="Collection for cosmetic surgeon data"
    )
    COSMETIC_SURGEON_SEARCH_INDEX_NAME: str = Field(
        default="search_index",
        description="Search index name for cosmetic surgeon"
    )
    COSMETIC_SURGEON_VECTOR_STORE: str = Field(
        default="Cosmetic_surgeon_vector_store",
        description="Vector store name for cosmetic surgeon"
    )

class AzureConfig(BaseModel):
    """Azure OpenAI configuration settings."""
    API_KEY: str = Field(
        default=st.secrets.azure_credential.get("AZURE_API_KEY", ""),
        description="Azure OpenAI API key"
    )
    BASE_URL: str = Field(
        default=st.secrets.azure_credential.get("AZURE_BASE_URL", ""),
        description="Azure OpenAI base URL"
    )
    API_VERSION: str = Field(
        default=st.secrets.azure_credential.get("AZURE_API_VERSION", ""),
        description="Azure OpenAI API version"
    )
    MODEL_NAME: str = Field(
        default=st.secrets.azure_credential.get("AZURE_MODEL_NAME", ""),
        description="Azure OpenAI model name"
    )

class RAGConfig(BaseModel):
    """RAG (Retrieval Augmented Generation) configuration settings."""
    TEXT_EMBEDDING_MODEL_ID: str = Field(
        default="BookingCare/gte-multilingual-base-v2.1",
        description="Text embedding model ID"
    )
    CHUNK_SIZE: int = Field(
        default=768,
        description="Chunk size for text splitting"
    )
    TOP_K: int = Field(
        default=5,
        description="Number of top results to retrieve"
    )
    DEVICE: str = Field(
        default="cpu",
        description="Device to run the model on"
    )

class CometConfig(BaseModel):
    """Comet ML configuration settings."""
    API_KEY: str = Field(
        default=st.secrets.comet_credential.get("COMET_API_KEY", ""),
        description="Comet ML API key"
    )
    WORKSPACE: str = Field(
        default=st.secrets.comet_credential.get("COMET_WORKSPACE", ""),
        description="Comet ML workspace"
    )
    PROJECT: str = Field(
        default="bookingcare",
        description="Comet ML project name"
    )

class MessageConfig(BaseModel):
    """Message handling configuration settings."""
    TOTAL_MESSAGES_SUMMARY_TRIGGER: int = Field(
        default=5,
        description="Number of messages before triggering summary"
    )
    TOTAL_MESSAGES_AFTER_SUMMARY: int = Field(
        default=3,
        description="Number of messages to keep after summary"
    )

class Config(BaseSettings):
    """Main configuration class that combines all settings."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    args: Optional[Any] = None
    mongo: MongoConfig = Field(default_factory=MongoConfig)
    azure: AzureConfig = Field(default_factory=AzureConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    comet: CometConfig = Field(default_factory=CometConfig)
    message: MessageConfig = Field(default_factory=MessageConfig)

    def init(self, args: InputArgs) -> None:
        """Initialize configuration with input arguments."""
        self.args = args

    def save_api_key(self, provider: str, **kwargs) -> None:
        """Save API keys to session state for persistence.
        
        Args:
            provider: The provider name ("OpenAI", "Azure OpenAI", or "Gemini")
            **kwargs: API key and related configuration values
        """
        if provider == "OpenAI":
            if "openai_api_key" in kwargs and kwargs["openai_api_key"]:
                st.session_state["openai_api_key_value"] = kwargs["openai_api_key"]
                st.session_state["openai_key_saved"] = True
                
        elif provider == "Azure OpenAI":
            if all(key in kwargs for key in ["AZURE_API_KEY", "AZURE_BASE_URL", "AZURE_API_VERSION"]):
                if kwargs["AZURE_API_KEY"] and kwargs["AZURE_BASE_URL"] and kwargs["AZURE_API_VERSION"]:
                    st.session_state["azure_api_key_value"] = kwargs["AZURE_API_KEY"]
                    st.session_state["azure_endpoint_value"] = kwargs["AZURE_BASE_URL"]
                    st.session_state["azure_deployment_value"] = kwargs["AZURE_API_VERSION"]
                    st.session_state["azure_keys_saved"] = True
                
        elif provider == "Gemini":
            if "gemini_api_key" in kwargs and kwargs["gemini_api_key"]:
                st.session_state["gemini_api_key_value"] = kwargs["gemini_api_key"]
                st.session_state["gemini_key_saved"] = True
    
    def get_api_key(self, provider: str) -> Dict[str, str]:
        """Retrieve API keys from session state.
        
        Args:
            provider: The provider name ("OpenAI", "Azure OpenAI", or "Gemini")
            
        Returns:
            Dictionary containing the API key(s) for the specified provider
        """
        if provider == "OpenAI":
            return {"openai_api_key": st.session_state.get("openai_api_key_value", "")}
            
        elif provider == "Azure OpenAI":
            return {
                "AZURE_API_KEY": st.session_state.get("azure_api_key_value", ""),
                "AZURE_BASE_URL": st.session_state.get("azure_endpoint_value", ""),
                "AZURE_API_VERSION": st.session_state.get("azure_deployment_value", "")
            }
            
        elif provider == "Gemini":
            return {"gemini_api_key": st.session_state.get("gemini_api_key_value", "")}
            
        return {}