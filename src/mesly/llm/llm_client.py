"""
LLM Client initialization and management
"""

from typing import Optional, Union, Literal

try:
    from google import genai
except ImportError:
    genai = None

try:
    import openai
except ImportError:
    openai = None

from ..config import ConfigTemplate, AIConfig, AIClient
from .exceptions import (
    AIConfigurationError,
    AIAPIKeyMissingError,
    AIProviderNotInstalledError,
    AIInitializationError
)


class LLMClientManager:
    """LLM Client bound to a specific provider"""

    def __init__(self, settings: Union[ConfigTemplate, AIConfig], provider: Literal["gemini", "openai"]):
        """
        Initialize LLM client for a specific provider

        Args:
            settings: ConfigTemplate or AIConfig object
            provider: Provider name ("gemini" or "openai")
        """
        if isinstance(settings, ConfigTemplate):
            self.ai_config = settings.ai
        else:
            self.ai_config = settings

        self.provider = provider
        self.config: Optional[AIClient] = self.ai_config.get_client(provider)
        self.client = None

        if self.config and self.config.enabled:
            self._initialize_client()
        else:
            print(f"Warning: {provider} client not found or not enabled in config")

    def _initialize_client(self):
        """Initialize the client based on provider"""
        if self.provider == "gemini":
            self.client = self._initialize_gemini()
        elif self.provider == "openai":
            self.client = self._initialize_openai()

    def _initialize_gemini(self) -> Optional[object]:
        """Initialize Google Gemini client"""
        if genai is None:
            raise AIProviderNotInstalledError("google-genai not installed. Install with: pip install google-genai")

        if not self.config.api_key:
            raise AIAPIKeyMissingError("No API key provided for Gemini client. Set api_key in config.")

        try:
            client = genai.Client(api_key=self.config.api_key)
            return client
        except Exception as e:
            raise AIInitializationError(f"Error initializing Gemini client: {e}")

    def _initialize_openai(self) -> Optional[object]:
        """Initialize OpenAI client"""
        if openai is None:
            raise AIProviderNotInstalledError("openai not installed. Install with: pip install openai")

        if not self.config.api_key:
            raise AIAPIKeyMissingError("No API key provided for OpenAI client. Set api_key in config.")

        try:
            client = openai.OpenAI(api_key=self.config.api_key)
            return client
        except Exception as e:
            raise AIInitializationError(f"Error initializing OpenAI client: {e}")

    def is_available(self) -> bool:
        """Check if client is properly initialized and available"""
        return self.client is not None and self.config is not None and self.config.enabled

    def generate(self, prompt: str) -> Optional[str]:
        """
        Generate text using this client's provider

        Args:
            prompt: Text prompt to generate from

        Returns:
            Generated text or None if failed
        """
        if not self.is_available():
            print(f"{self.provider} client not available")
            return None

        try:
            if self.provider == "gemini":
                return self._generate_gemini(prompt)
            elif self.provider == "openai":
                return self._generate_openai(prompt)
        except Exception as e:
            print(f"Error generating with {self.provider}: {e}")
            return None

    def _generate_gemini(self, prompt: str) -> Optional[str]:
        """Generate text using Gemini"""
        response = self.client.models.generate_content(
            model=self.config.model,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_tokens
            )
        )
        return response.text

    def _generate_openai(self, prompt: str) -> Optional[str]:
        """Generate text using OpenAI"""
        kwargs = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature
        }

        if self.config.max_tokens:
            kwargs["max_tokens"] = self.config.max_tokens

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
