"""
Mesly - OCR-based language learning tool for gaming
"""

from .utils import Logger, ModelSetup, HotkeyManager
from .capture import ScreenCapture
from .app import MeslyApp

__version__ = "0.1.0"
__author__ = "kaldwin"

# Global instances
_hotkey_manager = None
_screen_capture = None

# Initialize local models on import
def _initialize():
    """Initialize Mesly on first import"""
    Logger.info("Initializing Mesly...")
    ModelSetup.setup_local_models()

def get_hotkey_manager() -> HotkeyManager:
    """Get global hotkey manager instance"""
    global _hotkey_manager
    if _hotkey_manager is None:
        _hotkey_manager = HotkeyManager()
    return _hotkey_manager

def get_screen_capture() -> ScreenCapture:
    """Get global screen capture instance"""
    global _screen_capture
    if _screen_capture is None:
        _screen_capture = ScreenCapture()
    return _screen_capture

def shutdown():
    """Shutdown Mesly and cleanup resources"""
    Logger.info("Shutting down Mesly...")
    if _hotkey_manager:
        _hotkey_manager.stop()
    ModelSetup.stop_ollama_server()

# Auto-run on import
_initialize()

__all__ = [
    "Logger",
    "ModelSetup",
    "HotkeyManager",
    "ScreenCapture",
    "MeslyApp",
    "get_hotkey_manager",
    "get_screen_capture",
    "shutdown"
]
