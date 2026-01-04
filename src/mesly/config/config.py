"""
Configuration management for Mesly
"""

import json
from pathlib import Path
from typing import Optional, Dict

from .models import (
    OCRConfig,
    TranslationConfig,
    CaptureConfig,
    CaptureRegion,
    OverlayConfig,
    AIConfig,
    AIClient
)


class ConfigTemplate:
    """Main configuration template"""

    _instances: Dict[str, 'ConfigTemplate'] = {}

    def __init__(self, filepath: str = "config/config.json"):
        """
        Initialize configuration, loading from file or creating default

        Args:
            filepath: Path to config file (default: config/config.json)
        """
        self.filepath = Path(filepath)

        # Initialize with defaults
        self.ocr = OCRConfig()
        self.translation = TranslationConfig()
        self.capture = CaptureConfig()
        self.overlay = OverlayConfig()
        self.ai = AIConfig()

        # Load from file if exists, otherwise save defaults
        if self.filepath.exists():
            print(f"Loading configuration from {self.filepath}")
            self._load()
            print(f"Configuration loaded successfully")
        else:
            print(f"Configuration file not found at {self.filepath}")
            print(f"Creating default configuration...")
            self.save()
            print(f"Default configuration saved to {self.filepath}")

    def _load(self) -> None:
        """Load configuration from file"""
        data = json.loads(self.filepath.read_text())

        # Reconstruct AI config with clients list
        ai_data = data.get("ai", {})
        clients_data = ai_data.get("clients", [])
        self.ai = AIConfig(
            clients=[AIClient(**client) for client in clients_data] if clients_data else []
        )

        self.ocr = OCRConfig(**data.get("ocr", {}))
        self.translation = TranslationConfig(**data.get("translation", {}))
        self.capture = CaptureConfig(
            fps=data.get("capture", {}).get("fps", 1),
            region=CaptureRegion(**data.get("capture", {}).get("region", {}))
        )
        self.overlay = OverlayConfig(**data.get("overlay", {}))

    def save(self) -> None:
        """Save configuration to file"""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        config_dict = {
            "ocr": self.ocr.__dict__,
            "translation": self.translation.__dict__,
            "capture": {
                "fps": self.capture.fps,
                "region": self.capture.region.__dict__
            },
            "overlay": self.overlay.__dict__,
            "ai": {
                "clients": [client.__dict__ for client in self.ai.clients]
            }
        }

        json_str = json.dumps(config_dict, indent=2)
        self.filepath.write_text(json_str)
        print(f"Configuration saved to {self.filepath}")

    def to_json(self) -> str:
        """Convert config to JSON string"""
        config_dict = {
            "ocr": self.ocr.__dict__,
            "translation": self.translation.__dict__,
            "capture": {
                "fps": self.capture.fps,
                "region": self.capture.region.__dict__
            },
            "overlay": self.overlay.__dict__,
            "ai": {
                "clients": [client.__dict__ for client in self.ai.clients]
            }
        }
        return json.dumps(config_dict, indent=2)

    @classmethod
    def get_config(cls, filepath: str = "config/config.json") -> 'ConfigTemplate':
        """
        Get configuration instance - automatically loads or creates config file
        Uses singleton pattern to ensure config is only loaded once per filepath

        Args:
            filepath: Path to config file (default: config/config.json)

        Returns:
            Ready-to-use ConfigTemplate instance
        """
        # Normalize the filepath
        normalized_path = str(Path(filepath).resolve())

        # Return existing instance if already loaded
        if normalized_path in cls._instances:
            print(f"Using cached configuration from {filepath}")
            return cls._instances[normalized_path]

        # Create new instance and cache it
        instance = cls(filepath)
        cls._instances[normalized_path] = instance
        return instance
