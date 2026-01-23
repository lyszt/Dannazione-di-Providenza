"""
Configuration dataclass models
"""

from .ocr_config import OCRConfig
from .translation_config import TranslationConfig
from .capture_config import CaptureConfig, CaptureRegion
from .overlay_config import OverlayConfig
from .ai_config import AIConfig, AIClient
from .ai_config import LocalLLMClient

__all__ = [
    "OCRConfig",
    "TranslationConfig",
    "CaptureConfig",
    "CaptureRegion",
    "OverlayConfig",
    "AIConfig",
    "AIClient",
    "LocalLLMClient"
]
