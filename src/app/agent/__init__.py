from typing import Dict, List, Optional, Type
from src.app.agent.provider.azure_provider import AzureOpenAIProvider
from src.app.agent.provider.gemini_provider import GeminiProvider
from src.app.agent.provider.openai_provider import OpenAIProvider
from src.app.agent.provider.provider_base import AIProvider

class ProviderFactory:
    """Factory class to create and manage AI providers."""
    
    _providers: Dict[str, Type[AIProvider]] = {
        "OpenAI": OpenAIProvider,
        "Azure OpenAI": AzureOpenAIProvider,
        "Gemini": GeminiProvider,
    }
    
    @classmethod
    def get_provider_names(cls) -> List[str]:
        """Get a list of available provider names."""
        return list(cls._providers.keys())
    
    @classmethod
    def create_provider(cls, provider_name: str) -> Optional[AIProvider]:
        """Create a provider instance by name."""
        provider_class = cls._providers.get(provider_name)
        if provider_class:
            return provider_class()
        return None
    
    @classmethod
    def get_configured_provider(cls) -> Optional[AIProvider]:
        """Get the first configured provider."""
        for provider_name in cls.get_provider_names():
            provider = cls.create_provider(provider_name)
            if provider and provider.is_configured():
                return provider
        return None
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[AIProvider]) -> None:
        """Register a new provider class."""
        cls._providers[name] = provider_class