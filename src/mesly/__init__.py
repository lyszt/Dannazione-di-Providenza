"""
Mesly - OCR-based language learning tool for gaming
"""

from .utils import Logger, ModelSetup

__version__ = "0.1.0"
__author__ = "kaldwin"

# Initialize local models on import
def _initialize():
    """Initialize Mesly on first import"""
    Logger.info("Initializing Mesly...")
    ModelSetup.setup_local_models()

def shutdown():
    """Shutdown Mesly and cleanup resources"""
    Logger.info("Shutting down Mesly...")
    ModelSetup.stop_ollama_server()

# Auto-run on import
_initialize()

__all__ = ["Logger", "ModelSetup", "shutdown"]
