import streamlit as st
import litellm
from typing import Dict, Iterator, List

from src.agent.provider.provider_base import AIProvider


class AzureOpenAIProvider(AIProvider):
    """Implementation of the Azure OpenAI provider."""
    
    def get_name(self) -> str:
        return "Azure OpenAI"
    
    def is_configured(self) -> bool:
        """Check if Azure OpenAI credentials are configured."""
        creds = self.get_credentials()
        return all([
            creds.get("AZURE_API_KEY", ""),
            creds.get("AZURE_BASE_URL", ""),
            creds.get("AZURE_API_VERSION", "")
        ])
    
    def get_missing_config_message(self) -> str:
        return "Please add your Azure OpenAI details to continue."
    
    def get_credentials_from_secrets(self) -> Dict[str, str]:
        """Get Azure OpenAI credentials from secrets.toml."""
        try:
            # First try to get credentials from the azure_credential section
            if hasattr(st.secrets, "azure_credential"):
                return {
                    "AZURE_API_KEY": st.secrets.azure_credential.get("AZURE_API_KEY", ""),
                    "AZURE_BASE_URL": st.secrets.azure_credential.get("AZURE_BASE_URL", ""),
                    "AZURE_API_VERSION": st.secrets.azure_credential.get("AZURE_API_VERSION", "")
                }
            # Fall back to top-level keys if the section doesn't exist
            return {
                "AZURE_API_KEY": st.secrets.get("AZURE_API_KEY", ""),
                "AZURE_BASE_URL": st.secrets.get("AZURE_BASE_URL", ""),
                "AZURE_API_VERSION": st.secrets.get("AZURE_API_VERSION", "")
            }
        except (AttributeError, KeyError):
            return {
                "AZURE_API_KEY": "",
                "AZURE_BASE_URL": "",
                "AZURE_API_VERSION": ""
            }
    
    def get_credentials_from_session(self) -> Dict[str, str]:
        """Get Azure OpenAI credentials from session state."""
        return {
            "AZURE_API_KEY": st.session_state.get("azure_api_key_value", ""),
            "AZURE_BASE_URL": st.session_state.get("azure_endpoint_value", ""),
            "AZURE_API_VERSION": st.session_state.get("azure_deployment_value", "")
        }
    
    def are_credentials_valid(self, credentials: Dict[str, str]) -> bool:
        """Check if the given credentials are valid."""
        return all([
            credentials.get("AZURE_API_KEY", ""),
            credentials.get("AZURE_BASE_URL", ""),
            credentials.get("AZURE_API_VERSION", "")
        ])
    
    def save_credentials_to_session(self, **kwargs) -> None:
        """Save Azure OpenAI credentials to session state."""
        if all(key in kwargs for key in ["AZURE_API_KEY", "AZURE_BASE_URL", "AZURE_API_VERSION"]):
            if kwargs["AZURE_API_KEY"] and kwargs["AZURE_BASE_URL"] and kwargs["AZURE_API_VERSION"]:
                st.session_state["azure_api_key_value"] = kwargs["AZURE_API_KEY"]
                st.session_state["azure_endpoint_value"] = kwargs["AZURE_BASE_URL"]
                st.session_state["azure_deployment_value"] = kwargs["AZURE_API_VERSION"]
                st.session_state["azure_keys_saved"] = True
    
    def generate_response(self, messages: List[Dict[str, str]], 
                          stream: bool = True) -> Iterator[str]:
        """Generate a response using Azure OpenAI's API."""
        creds = self.get_credentials()
        
        for chunk in litellm.completion(
            model="azure/gpt-4.1-nano",
            api_key=creds["AZURE_API_KEY"],
            api_base=creds["AZURE_BASE_URL"],
            api_version=creds["AZURE_API_VERSION"],
            messages=messages,
            stream=stream,
        ):
            if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                content_chunk = chunk.choices[0].delta.content
                yield content_chunk