"""
Translation configuration dataclass
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TranslationConfig:
    """Translation service configuration"""
    service: str = "google"  # google, deepl
    source_language: str = "auto"
    target_language: str = "en"
    cache_enabled: bool = True
    api_key: Optional[str] = None
