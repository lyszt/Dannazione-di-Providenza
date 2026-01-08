import os
import sys
from datetime import datetime
from pathlib import Path
import pytesseract
import easygui
from PIL import Image
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from .config.config import ConfigTemplate
from .utils import Logger, HotkeyManager
from .capture import ScreenCapture
from .window.main_window import MainWindow
from .config.prompts import LanguageTutorPrompts
from .server.server import Server
from .agent.agent import Agent

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

        # Initialize Agent with AI client
        Logger.info("Initializing Agent...")
        self.agent = Agent(self.config)

        if not self.agent.is_ready():
            Logger.error(f"Agent not ready. Please check your config at config/config.yaml")
        else:
            Logger.info("Agent initialized and ready")

        self.window = MainWindow(self.agent)
        self.window.show()

        # Start hotkey listeners
        self.hotkey_manager.start()
        Logger.info("Hotkey listener started - Ctrl+Alt+S to screenshot")

        self.server = Server(
            host="127.0.0.1",
            port=8000,
            agent=self.agent,
            config=self.config,
            screen_capture=self.screen_capture
        )
        self.server.start()
        Logger.info("FastAPI server started on http://127.0.0.1:8000")

        sys.exit(app.exec())

    def _register_hotkeys(self):
        """Register Ctrl+Alt+S for screenshot"""
        self.hotkey_manager.register(
            '<ctrl>+<alt>+s',
            self._on_screenshot_hotkey
        )
        Logger.info("Registered hotkey: Ctrl+Alt+S (Screenshot)")

    def _on_screenshot_hotkey(self):
        """Handle screenshot hotkey press (runs in hotkey thread)"""
        Logger.info("Screenshot hotkey pressed (Ctrl+Alt+S)")
        # Emit signal to capture screenshot in main thread
        self.signals.screenshot_requested.emit()

    def _capture_screenshot(self):
        """Capture screenshot (runs in main thread)"""
        screenshot_path = Path(__file__).resolve().parent.parent.parent / "data" / "screenshots"
        screenshot_path.mkdir(parents=True, exist_ok=True)

        for item in screenshot_path.iterdir():
            if item.is_file():
                item.unlink()

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

            # Perform OCR on the screenshot
            try:
                Logger.info("Performing OCR on screenshot...")
                with Image.open(filepath) as img:
                    ocr_text = pytesseract.image_to_string(img).strip()

                if ocr_text:
                    Logger.info(f"OCR extracted {len(ocr_text)} characters")

                    # Show popup to ask user what they want to know
                    user_question = easygui.enterbox(
                        msg=f"OCR Text found:\n\n{ocr_text[:200]}{'...' if len(ocr_text) > 200 else ''}\n\nWhat do you want to ask about this text?",
                        title="Mesly - Ask AI",
                        default=""
                    )

                    if user_question:
                        Logger.info(f"User question: {user_question}")

                        # Process screenshot inquiry through Agent
                        # Window will handle the UI and audio presentation
                        self.window.process_screenshot_inquiry(ocr_text, user_question)
                    else:
                        Logger.info("User cancelled prompt")
                        self.window.lbl_status.setText("Screenshot captured, no AI request")
                else:
                    Logger.warning("No text found in screenshot")
                    easygui.msgbox("No text detected in screenshot", "Mesly - OCR")

            except Exception as e:
                Logger.error(f"OCR or AI processing failed: {e}")
                easygui.msgbox(f"Error processing screenshot: {e}", "Mesly - Error")
        else:
            Logger.error("Failed to capture screenshot")



