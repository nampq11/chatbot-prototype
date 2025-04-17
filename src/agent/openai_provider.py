import os
import streamlit as st
import litellm
from typing import Dict, Iterator, List

from src.agent.provider_base import AIProvider


class OpenAIProvider(AIProvider):
    """Implementation of the OpenAI provider."""
    
    def get_name(self) -> str:
        return "OpenAI"
    
    def is_configured(self) -> bool:
        """Check if OpenAI API key is configured."""
        creds = self.get_credentials()
        return bool(creds.get("openai_api_key", ""))
    
    def get_missing_config_message(self) -> str:
        return "Please add your OpenAI API key to continue."
    
    def get_credentials_from_secrets(self) -> Dict[str, str]:
        """Get OpenAI API key from secrets.toml."""
        try:
            # First try to get credentials from openai_credential section
            if hasattr(st.secrets, "openai_credential"):
                return {"openai_api_key": st.secrets.openai_credential.get("OPENAI_API_KEY", "")}
            # Fall back to top-level keys
            return {"openai_api_key": st.secrets.get("OPENAI_API_KEY", "")}
        except (AttributeError, KeyError):
            return {"openai_api_key": ""}
    
    def get_credentials_from_session(self) -> Dict[str, str]:
        """Get OpenAI API key from session state."""
        return {"openai_api_key": st.session_state.get("openai_api_key_value", "")}
    
    def are_credentials_valid(self, credentials: Dict[str, str]) -> bool:
        """Check if the given credentials are valid."""
        return bool(credentials.get("openai_api_key", ""))
    
    def save_credentials_to_session(self, **kwargs) -> None:
        """Save OpenAI API key to session state."""
        if "openai_api_key" in kwargs and kwargs["openai_api_key"]:
            st.session_state["openai_api_key_value"] = kwargs["openai_api_key"]
            st.session_state["openai_key_saved"] = True
            os.environ["OPENAI_API_KEY"] = kwargs["openai_api_key"]
    
    def generate_response(self, messages: List[Dict[str, str]], 
                          stream: bool = True) -> Iterator[str]:
        """Generate a response using OpenAI's API."""
        api_key = self.get_credentials().get("openai_api_key", "")
        os.environ["OPENAI_API_KEY"] = api_key
        
        for chunk in litellm.completion(
            model="gpt-4.1-nano",
            messages=messages,
            stream=stream,
        ):
            if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                content_chunk = chunk.choices[0].delta.content
                yield content_chunk