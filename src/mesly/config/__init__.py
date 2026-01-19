"""
Configuration management package
"""

from .config import ConfigTemplate
from .models import (
    OCRConfig,
    TranslationConfig,
    CaptureConfig,
    CaptureRegion,
    OverlayConfig,
    AIConfig,
    AIClient
)
from .prompts import ProvidentiaPrompts, get_prompt

__all__ = [
    "ConfigTemplate",
    "OCRConfig",
    "TranslationConfig",
    "CaptureConfig",
    "CaptureRegion",
    "OverlayConfig",
    "AIConfig",
    "AIClient",
    "ProvidentiaPrompts",
    "get_prompt"
]
