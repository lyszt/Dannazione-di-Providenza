"""
Generative AI configuration dataclasses
"""

from dataclasses import dataclass, field
from typing import Optional, Literal, List

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
class AIConfig:
    """Main AI configuration - holds multiple clients"""
    clients: List[AIClient] = field(default_factory=list)

    def __post_init__(self):
        """Initialize with default clients if empty"""
        if not self.clients:
            self.clients = [
                AIClient(provider="gemini", model="gemini-2.0-flash-exp", enabled=False),
                AIClient(provider="openai", model="gpt-4o-mini", enabled=False)
            ]

    def get_enabled_clients(self) -> List[AIClient]:
        """Get all enabled clients"""
        return [client for client in self.clients if client.enabled]

    def get_client(self, provider: str) -> Optional[AIClient]:
        """Get client by provider name"""
        for client in self.clients:
            if client.provider == provider:
                return client
        return None
