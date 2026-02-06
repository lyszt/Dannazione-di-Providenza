"""
Configuration management package
"""

from .config import ConfigTemplate
from .gpuconfig import GPUConfig
from .specs import SystemSpecs
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
    "GPUConfig",
    "SystemSpecs",
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
