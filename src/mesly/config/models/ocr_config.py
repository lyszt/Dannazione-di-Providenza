"""
OCR configuration dataclass
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class OCRConfig:
    """OCR engine configuration"""
    engine: str = "easyocr"  # easyocr, pytesseract, paddleocr
    languages: List[str] = field(default_factory=lambda: ["ja", "en"])
    confidence_threshold: float = 0.5
    use_gpu: bool = False
