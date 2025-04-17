import streamlit as st
from typing import Dict, Iterator, List
from google import genai

from src.agent.provider_base import AIProvider


class GeminiProvider(AIProvider):
    """Implementation of the Gemini provider."""
    
    def get_name(self) -> str:
        return "Gemini"
    
    def is_configured(self) -> bool:
        """Check if Gemini API key is configured."""
        creds = self.get_credentials()
        return bool(creds.get("gemini_api_key", ""))
    
    def get_missing_config_message(self) -> str:
        return "Please add your Gemini API key to continue."
    
    def get_credentials_from_secrets(self) -> Dict[str, str]:
        """Get Gemini API key from secrets.toml."""
        try:
            # First try to get credentials from gemini_credential section
            if hasattr(st.secrets, "gemini_credential"):
                return {"gemini_api_key": st.secrets.gemini_credential.get("GEMINI_API_KEY", "")}
            # Fall back to top-level keys
            return {"gemini_api_key": st.secrets.get("GEMINI_API_KEY", "")}
        except (AttributeError, KeyError):
            return {"gemini_api_key": ""}
    
    def get_credentials_from_session(self) -> Dict[str, str]:
        """Get Gemini API key from session state."""
        return {"gemini_api_key": st.session_state.get("gemini_api_key_value", "")}
    
    def are_credentials_valid(self, credentials: Dict[str, str]) -> bool:
        """Check if the given credentials are valid."""
        return bool(credentials.get("gemini_api_key", ""))
    
    def save_credentials_to_session(self, **kwargs) -> None:
        """Save Gemini API key to session state."""
        if "gemini_api_key" in kwargs and kwargs["gemini_api_key"]:
            st.session_state["gemini_api_key_value"] = kwargs["gemini_api_key"]
            st.session_state["gemini_key_saved"] = True
    
    def generate_response(self, messages: List[Dict[str, str]], 
                          stream: bool = True) -> Iterator[str]:
        """Generate a response using Gemini's API."""
        try:
            api_key = self.get_credentials().get("gemini_api_key", "")
            genai.configure(api_key=api_key)
            
            model = genai.GenerativeModel('gemini-pro')
            
            gemini_messages = []
            for message in messages:
                role = "user" if message["role"] == "user" else "model"
                gemini_messages.append({"role": role, "parts": [message["content"]]})
            
            response = model.generate_content(gemini_messages, stream=stream)
            
            for chunk in response:
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
                    
        except ImportError:
            yield "Error: google-genai package not installed. Please contact the administrator."
        except Exception as e:
            yield f"I encountered an error while processing your request: {str(e)}"