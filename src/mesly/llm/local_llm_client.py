"""
Local LLM Client initialization and management
"""

from typing import Optional, Union, Literal

try:
    import ollama
except ImportError:
    ollama = None

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

from ..config import ConfigTemplate, AIConfig
from ..config.models.ai_config import LocalLLMClient
from ..utils import Logger
from .exceptions import (
    AIConfigurationError,
    AIAPIKeyMissingError,
    AIProviderNotInstalledError,
    AIInitializationError
)


class LocalLLMClientManager:
    """Local LLM Client bound to a specific provider"""

    def __init__(self, settings: Union[ConfigTemplate, AIConfig], provider: Literal["ollama", "llamacpp"]):
        """
        Initialize Local LLM client for a specific provider

        Args:
            settings: ConfigTemplate or AIConfig object
            provider: Provider name ("ollama" or "llamacpp")
        """
        if isinstance(settings, ConfigTemplate):
            self.ai_config = settings.ai
        else:
            self.ai_config = settings

        self.provider = provider
        self.config: Optional[LocalLLMClient] = self.ai_config.get_local_client(provider)
        self.client = None

        if self.config and self.config.enabled:
            self._initialize_client()
            Logger.info(f"{provider.capitalize()} local client initialized successfully")
        else:
            Logger.warning(f"{provider} local client not found or not enabled in config")

    def _initialize_client(self):
        """Initialize the client based on provider"""
        if self.provider == "ollama":
            self.client = self._initialize_ollama()
        elif self.provider == "llamacpp":
            self.client = self._initialize_llamacpp()

    def _initialize_ollama(self) -> Optional[object]:
        """Initialize Ollama client"""
        if ollama is None:
            raise AIProviderNotInstalledError("ollama not installed. Install with: pip install ollama")

        try:
            # Ollama client is lightweight, no need to initialize
            Logger.info(f"Ollama client ready - Host: {self.config.host}, Model: {self.config.model}")
            return ollama
        except Exception as e:
            raise AIInitializationError(f"Error initializing Ollama client: {e}")

    def _initialize_llamacpp(self) -> Optional[object]:
        """Initialize llama-cpp-python client"""
        if Llama is None:
            raise AIProviderNotInstalledError("llama-cpp-python not installed. Install with: pip install llama-cpp-python")

        if not self.config.model_path:
            raise AIConfigurationError("model_path is required for llamacpp provider. Set model_path in config.")

        try:
            client = Llama(
                model_path=self.config.model_path,
                n_ctx=2048,
                n_threads=4
            )
            Logger.info(f"Llama.cpp client loaded - Model: {self.config.model_path}")
            return client
        except Exception as e:
            raise AIInitializationError(f"Error initializing Llama.cpp client: {e}")

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
            Logger.error(f"{self.provider} local client not available")
            return None

        try:
            Logger.debug(f"Generating with {self.provider}: {prompt[:50]}...")
            if self.provider == "ollama":
                return self._generate_ollama(prompt)
            elif self.provider == "llamacpp":
                return self._generate_llamacpp(prompt)
        except Exception as e:
            Logger.exception(f"Error generating with {self.provider}: {e}")
            return None

    def _generate_ollama(self, prompt: str) -> Optional[str]:
        """Generate text using Ollama"""
        response = self.client.chat(
            model=self.config.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens if self.config.max_tokens else -1
            }
        )
        return response['message']['content']

    def _generate_llamacpp(self, prompt: str) -> Optional[str]:
        """Generate text using Llama.cpp"""
        kwargs = {
            "prompt": prompt,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens if self.config.max_tokens else 512
        }

        response = self.client(**kwargs)
        return response['choices'][0]['text']
