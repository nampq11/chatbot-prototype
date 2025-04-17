from typing import Optional, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import streamlit as st


class InputArgs(BaseModel):
    AZURE_API_KEY: str
    AZURE_BASE_URL: str
    AZURE_API_VERSION: str
    openai_api_key: str
    gemini_api_key: str 

class Config(BaseModel):
    args: Optional[Any] = None
    MONGO_URI: str = Field(
        default="mongodb+srv://nampham11062002:Phamnamaq123@@cluster0.t13jleh.mongodb.net/?appName=Cluster0"
    )
    MONGO_DB_NAME: str = "bkcare"
    MONGO_STATE_CHECKPOINT_COLLECTION: str = "bkcare_state_checkpoints"
    MONGO_STATE_WRITES_COLLECTION: str = "bkcare_state_writes"
    MONGO_LONG_TERM_MEMORY_COLLECTION: str = "bkcare_long_term_memory"
    
    def init(self, args):
        self.args = args
    
    def save_api_key(self, provider: str, **kwargs):
        """Save API keys to session state for persistence"""
        if provider == "OpenAI":
            if "openai_api_key" in kwargs and kwargs["openai_api_key"]:
                st.session_state["openai_api_key_value"] = kwargs["openai_api_key"]
                # Hide the key after saving
                st.session_state["openai_key_saved"] = True
                
        elif provider == "Azure OpenAI":
            if all(key in kwargs for key in ["AZURE_API_KEY", "AZURE_BASE_URL", "AZURE_API_VERSION"]):
                if kwargs["AZURE_API_KEY"] and kwargs["AZURE_BASE_URL"] and kwargs["AZURE_API_VERSION"]:
                    st.session_state["azure_api_key_value"] = kwargs["AZURE_API_KEY"]
                    st.session_state["azure_endpoint_value"] = kwargs["AZURE_BASE_URL"]
                    st.session_state["azure_deployment_value"] = kwargs["AZURE_API_VERSION"]
                    # Hide the keys after saving
                    st.session_state["azure_keys_saved"] = True
                
        elif provider == "Gemini":
            if "gemini_api_key" in kwargs and kwargs["gemini_api_key"]:
                st.session_state["gemini_api_key_value"] = kwargs["gemini_api_key"]
                # Hide the key after saving
                st.session_state["gemini_key_saved"] = True
    
    def get_api_key(self, provider: str) -> dict:
        """Retrieve API keys from session state"""
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