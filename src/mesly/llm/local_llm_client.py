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
            Logger.warning(f"{provider} local client not found or not enabled in index")

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

    def generate(self, prompt: str, system_prompt: Optional[str] = None, stream_callback=None) -> Optional[str]:
        """
        Generate text using this client's provider

        Args:
            prompt: Text prompt to generate from
            system_prompt: Optional system prompt for agent
            stream_callback: Optional callback function(chunk: str) for streaming responses

        Returns:
            Generated text or None if failed
        """
        if not self.is_available():
            Logger.error(f"{self.provider} local client not available")
            return None

        try:
            Logger.debug(f"Generating with {self.provider}: {prompt[:50]}...")
            if self.provider == "ollama":
                return self._generate_ollama(prompt, system_prompt, stream_callback)
            elif self.provider == "llamacpp":
                return self._generate_llamacpp(prompt, system_prompt, stream_callback)
        except Exception as e:
            Logger.exception(f"Error generating with {self.provider}: {e}")
            return None

    def _generate_ollama(self, prompt: str, system_prompt: Optional[str] = None, stream_callback=None) -> Optional[str]:
        """Generate text using Ollama with optional streaming"""
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            Logger.info(f"Using system prompt: {system_prompt[:100]}...")

        messages.append({"role": "user", "content": prompt})
        Logger.info(f"Generating with Ollama model '{self.config.model}' (temp={self.config.temperature})...")

        # Use streaming if callback provided
        if stream_callback:
            full_response = ""
            stream = self.client.chat(
                model=self.config.model,
                messages=messages,
                stream=True,
                options={
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens if self.config.max_tokens else -1
                }
            )

            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    full_response += content
                    stream_callback(content)

            Logger.info(f"Ollama generation complete: {len(full_response)} chars")
            return full_response
        else:
            # Non-streaming mode
            response = self.client.chat(
                model=self.config.model,
                messages=messages,
                options={
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens if self.config.max_tokens else -1
                }
            )

            Logger.info(f"Ollama generation complete: {len(response['message']['content'])} chars")
            return response['message']['content']

    def _generate_llamacpp(self, prompt: str, system_prompt: Optional[str] = None, stream_callback=None) -> Optional[str]:
        """Generate text using Llama.cpp with optional streaming"""
        # Combine system prompt with user prompt for llama.cpp
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
            Logger.info(f"Using system prompt: {system_prompt[:100]}...")

        kwargs = {
            "prompt": full_prompt,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens if self.config.max_tokens else 512,
            "stream": stream_callback is not None
        }

        Logger.info(f"Generating with Llama.cpp (temp={self.config.temperature}, max_tokens={kwargs['max_tokens']})...")

        if stream_callback:
            full_response = ""
            for chunk in self.client(**kwargs):
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    text = chunk['choices'][0].get('text', '')
                    full_response += text
                    stream_callback(text)

            Logger.info(f"Llama.cpp generation complete: {len(full_response)} chars")
            return full_response
        else:
            response = self.client(**kwargs)
            result_text = response['choices'][0]['text']
            Logger.info(f"Llama.cpp generation complete: {len(result_text)} chars")
            return result_text
