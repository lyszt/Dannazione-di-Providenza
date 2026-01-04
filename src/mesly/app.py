import sys
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal

from .config.config import ConfigTemplate
from .utils import Logger, HotkeyManager
from .capture import ScreenCapture
from .window.main_window import MainWindow

__version__ = "0.1.0"


class HotkeySignals(QObject):
    """Qt signals for thread-safe hotkey handling"""
    screenshot_requested = pyqtSignal()


class MeslyApp:
    def __init__(self):
        print("MeslyApp v%s" % __version__)
        print("Initializing Mesly...")
        self.config = ConfigTemplate.get_config()

        # Setup hotkeys
        self.hotkey_manager = HotkeyManager()
        self.screen_capture = ScreenCapture()

        # Signal handler for thread-safe screenshot
        self.signals = HotkeySignals()
        self.signals.screenshot_requested.connect(self._capture_screenshot)

        self._register_hotkeys()

        app = QApplication(sys.argv)
        app.setApplicationName("Mesly")
        app.setStyle("Fusion")

        self.window = MainWindow()
        self.window.show()

        # Start hotkey listener
        self.hotkey_manager.start()
        Logger.info("Hotkey listener started - Ctrl+Shift+T to screenshot")

        sys.exit(app.exec())

    def _register_hotkeys(self):
        """Register Ctrl+Shift+T for screenshot"""
        self.hotkey_manager.register(
            '<ctrl>+<shift>+t',
            self._on_screenshot_hotkey
        )
        Logger.info("Registered hotkey: Ctrl+Shift+T (Screenshot)")

    def _on_screenshot_hotkey(self):
        """Handle screenshot hotkey press (runs in hotkey thread)"""
        Logger.info("Screenshot hotkey pressed (Ctrl+Shift+T)")
        # Emit signal to capture screenshot in main thread
        self.signals.screenshot_requested.emit()

    def _capture_screenshot(self):
        """Capture screenshot (runs in main thread)"""
        from PyQt5.QtCore import QTimer

        # Minimize window to avoid capturing it
        was_minimized = self.window.isMinimized()
        if not was_minimized:
            self.window.showMinimized()

        # Small delay to let window minimize and X11 to settle
        QTimer.singleShot(100, self._do_capture)

    def _do_capture(self):
        """Actually perform the capture after delay"""
        # Generate filepath with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"data/screenshots/screenshot_{timestamp}.png"

        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        # Capture and save
        success = self.screen_capture.capture_and_save(filepath)

        # Restore window
        self.window.showNormal()

        if success:
            Logger.info(f"Screenshot saved: {filepath}")
        else:
            Logger.error("Failed to capture screenshot")