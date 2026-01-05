import time
import numpy as np
import pytesseract
from PyQt5.QtCore import QThread, pyqtSignal
from PIL import Image

from .screen_capture import ScreenCapture
from ..utils import Logger


class ScreenShareThread(QThread):
    """
    Captures fullscreen at regular intervals and performs OCR.
    Simplified to only support fullscreen capture.
    """
    # Signal: (Image Object, Extracted Text String)
    content_update = pyqtSignal(object, str)

    def __init__(self):
        super().__init__()
        self.interval = 2.0
        self.running = True
        self.capture_tool = ScreenCapture()
        self.last_frame = None

    def run(self):
        Logger.info("Starting fullscreen capture stream")

        while self.running:
            start_time = time.time()

            # Capture fullscreen (no region parameter)
            frame_arr = self.capture_tool.capture_screen()

            if frame_arr is not None:
                if self._is_different(frame_arr):
                    # Convert to PIL
                    img = Image.fromarray(frame_arr)
                    text_content = ""

                    try:
                        # Tesseract reads the text from the RAM image
                        text_content = pytesseract.image_to_string(img).strip()
                        Logger.debug(f"OCR extracted {len(text_content)} chars")
                    except Exception as e:
                        Logger.error(f"OCR Failed: {e}")

                    self.content_update.emit(img, text_content)
                    self.last_frame = frame_arr

            elapsed = time.time() - start_time
            time.sleep(max(0.1, self.interval - elapsed))

    def _is_different(self, current):
        if self.last_frame is None:
            return True
        if current.shape != self.last_frame.shape:
            return True
        return not np.array_equal(current, self.last_frame)

    def stop(self):
        self.running = False
        self.wait()

