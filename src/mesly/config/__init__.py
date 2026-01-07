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
from .prompts import LanguageTutorPrompts, get_tutor_prompt

__all__ = [
    "ConfigTemplate",
    "OCRConfig",
    "TranslationConfig",
    "CaptureConfig",
    "CaptureRegion",
    "OverlayConfig",
    "AIConfig",
    "AIClient",
    "LanguageTutorPrompts",
    "get_tutor_prompt"
]
