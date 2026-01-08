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
from ..utils import Logger
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
            Logger.info(f"{provider.capitalize()} client initialized successfully")
        else:
            Logger.warning(f"{provider} client not found or not enabled in index")

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
            raise AIAPIKeyMissingError("No API key provided for Gemini client. Set api_key in index.")

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

    def generate(self, prompt: str, system_prompt: Optional[str] = None, stream_callback=None) -> Optional[str]:
        """
        Generate text using this client's provider

        Args:
            prompt: Text prompt to generate from
            system_prompt: Optional system prompt for context
            stream_callback: Optional callback function(chunk: str) for streaming responses

        Returns:
            Generated text or None if failed
        """
        if not self.is_available():
            Logger.error(f"{self.provider} client not available")
            return None

        try:
            Logger.debug(f"Generating with {self.provider}: {prompt[:50]}...")
            if self.provider == "gemini":
                return self._generate_gemini(prompt, system_prompt, stream_callback)
            elif self.provider == "openai":
                return self._generate_openai(prompt, system_prompt, stream_callback)
        except Exception as e:
            Logger.exception(f"Error generating with {self.provider}: {e}")
            return None

    def _generate_gemini(self, prompt: str, system_prompt: Optional[str] = None, stream_callback=None) -> Optional[str]:
        """Generate text using Gemini with optional streaming"""
        # Combine system prompt with user prompt for Gemini
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
            Logger.info(f"Using system prompt: {system_prompt[:100]}...")

        Logger.info(f"Generating with Gemini model '{self.config.model}' (temp={self.config.temperature})...")

        config = genai.types.GenerateContentConfig(
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_tokens
        )

        if stream_callback:
            full_response = ""
            response_stream = self.client.models.generate_content_stream(
                model=self.config.model,
                contents=full_prompt,
                config=config
            )

            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    stream_callback(chunk.text)

            Logger.info(f"Gemini generation complete: {len(full_response)} chars")
            return full_response
        else:
            response = self.client.models.generate_content(
                model=self.config.model,
                contents=full_prompt,
                config=config
            )
            Logger.info(f"Gemini generation complete: {len(response.text)} chars")
            return response.text

    def _generate_openai(self, prompt: str, system_prompt: Optional[str] = None, stream_callback=None) -> Optional[str]:
        """Generate text using OpenAI with optional streaming"""
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            Logger.info(f"Using system prompt: {system_prompt[:100]}...")

        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "stream": stream_callback is not None
        }

        if self.config.max_tokens:
            kwargs["max_tokens"] = self.config.max_tokens

        Logger.info(f"Generating with OpenAI model '{self.config.model}' (temp={self.config.temperature})...")

        if stream_callback:
            full_response = ""
            stream = self.client.chat.completions.create(**kwargs)

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    stream_callback(content)

            Logger.info(f"OpenAI generation complete: {len(full_response)} chars")
            return full_response
        else:
            response = self.client.chat.completions.create(**kwargs)
            result = response.choices[0].message.content
            Logger.info(f"OpenAI generation complete: {len(result)} chars")
            return result
