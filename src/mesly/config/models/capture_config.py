"""
Capture configuration dataclasses
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CaptureRegion:
    """Screen capture region"""
    x: Optional[int] = None
    y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None


@dataclass
class CaptureConfig:
    """Screen capture configuration"""
    fps: int = 1
    region: CaptureRegion = field(default_factory=CaptureRegion)
