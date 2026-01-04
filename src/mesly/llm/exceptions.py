"""
LLM client exceptions
"""


class AIConfigurationError(Exception):
    """Base exception for AI configuration errors"""
    pass


class AIAPIKeyMissingError(AIConfigurationError):
    """Raised when API key is not provided in configuration"""
    pass


class AIProviderNotInstalledError(AIConfigurationError):
    """Raised when required provider package is not installed"""
    pass


class AIInitializationError(AIConfigurationError):
    """Raised when AI client fails to initialize"""
    pass
