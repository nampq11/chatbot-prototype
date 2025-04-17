from abc import ABC, abstractmethod
from typing import Dict, Iterator, List, Optional
import streamlit as st

class ChatMessage:
    """Represents a message in a chat conversation."""
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
    
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "ChatMessage":
        return cls(role=data["role"], content=data["content"])

class AIProvider(ABC):
    """Base class for all AI providers."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the provider."""
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider is properly configured."""
        pass
    
    @abstractmethod
    def get_missing_config_message(self) -> str:
        """Return a message about missing configuration."""
        pass
    
    @abstractmethod
    def get_credentials_from_secrets(self) -> Dict[str, str]:
        """Get credentials from secrets.toml file."""
        pass
    
    @abstractmethod
    def get_credentials_from_session(self) -> Dict[str, str]:
        """Get credentials from session state."""
        pass
    
    def get_credentials(self) -> Dict[str, str]:
        """Get credentials from secrets.toml first, then session state."""
        # Try to get credentials from secrets.toml first
        secrets_creds = self.get_credentials_from_secrets()
        if self.are_credentials_valid(secrets_creds):
            return secrets_creds
            
        # Fall back to session state if secrets aren't valid
        return self.get_credentials_from_session()
    
    @abstractmethod
    def are_credentials_valid(self, credentials: Dict[str, str]) -> bool:
        """Check if the given credentials are valid."""
        pass
    
    @abstractmethod
    def save_credentials_to_session(self, **kwargs) -> None:
        """Save credentials to session state."""
        pass
    
    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]], 
                          stream: bool = True) -> Iterator[str]:
        """Generate a response from the AI based on the message history."""
        pass