"""
Generative AI configuration dataclasses
"""

from dataclasses import dataclass, field
from typing import Optional, Literal, List, Union

try:
    from google import genai
except ImportError:
    genai = None

try:
    import openai
except ImportError:
    openai = None


@dataclass
class AIClient:
    """Individual AI client configuration"""
    provider: Literal["gemini", "openai"]
    api_key: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    enabled: bool = True


@dataclass
class LocalLLMClient:
    """Individual local LLM client configuration"""
    provider: Literal["ollama", "llamacpp"]
    model: str = "llama2"
    model_path: Optional[str] = None  # For llamacpp
    host: str = "http://localhost:11434"  # For ollama
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    enabled: bool = True


@dataclass
class AIConfig:
    """Main AI configuration - holds multiple clients"""
    clients: List[AIClient] = field(default_factory=list)
    local_clients: List[LocalLLMClient] = field(default_factory=list)

    def __post_init__(self):
        """Initialize with default clients if empty"""
        if not self.clients:
            self.clients = [
                AIClient(provider="gemini", model="gemini-2.0-flash-exp", enabled=False),
                AIClient(provider="openai", model="gpt-4o-mini", enabled=False)
            ]
        if not self.local_clients:
            self.local_clients = [
                LocalLLMClient(provider="ollama", model="phi3.5", enabled=True),
                LocalLLMClient(provider="llamacpp", model="llama2", enabled=False)
            ]

    def get_enabled_clients(self) -> List[AIClient]:
        """Get all enabled cloud clients"""
        return [client for client in self.clients if client.enabled]

    def get_enabled_local_clients(self) -> List[LocalLLMClient]:
        """Get all enabled local clients"""
        return [client for client in self.local_clients if client.enabled]

    def get_client(self, provider: str) -> Optional[AIClient]:
        """Get cloud client by provider name"""
        for client in self.clients:
            if client.provider == provider:
                return client
        return None

    def get_local_client(self, provider: str) -> Optional[LocalLLMClient]:
        """Get local client by provider name"""
        for client in self.local_clients:
            if client.provider == provider:
                return client
        return None
