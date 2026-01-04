import time
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from PIL import Image

from .screen_capture import ScreenCapture
from .window_selector import WindowSelector
from ..utils import Logger


class ScreenShareThread(QThread):
    frame_captured = pyqtSignal(object)

    def __init__(self, target_window_title=None):
        super().__init__()
        self.target_window = target_window_title
        self.interval = 2.0
        self.running = True

        self.capture_tool = ScreenCapture()
        self.selector = WindowSelector()
        self.last_frame = None

        # Helper to avoid spamming logs
        self._log_cooldown = 0

    def run(self):
        Logger.info(f"Starting stream for window: {self.target_window}")

        while self.running:
            start_time = time.time()
            region = None

            if self.target_window:
                region = self.selector.get_window_geometry(self.target_window)

                if not region:
                    if time.time() - self._log_cooldown > 10:
                        Logger.info(f"Window '{self.target_window}' is minimized/hidden. Pausing stream...")
                        self._log_cooldown = time.time()

                    time.sleep(1.0)  # Check again in 1s
                    continue

            frame_arr = self.capture_tool.capture_screen(region=region)

            if frame_arr is not None:
                if self._is_different(frame_arr):
                    img = Image.fromarray(frame_arr)
                    self.frame_captured.emit(img)
                    self.last_frame = frame_arr
                    if self._log_cooldown > 0:
                        Logger.info(f"Window '{self.target_window}' restored. Stream resuming.")
                        self._log_cooldown = 0

            # --- 3. TIMING ---
            elapsed = time.time() - start_time
            sleep_time = max(0.1, self.interval - elapsed)
            time.sleep(sleep_time)

    def _is_different(self, current):
        if self.last_frame is None: return True
        if current.shape != self.last_frame.shape: return True
        return not np.array_equal(current, self.last_frame)

    def stop(self):
        self.running = False
        self.wait()