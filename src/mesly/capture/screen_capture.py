"""
Screen capture functionality
"""

import numpy as np
from PIL import Image
from typing import Optional, Tuple
from ..utils import Logger

try:
    import mss
    HAS_MSS = True
except ImportError:
    HAS_MSS = False

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False


class ScreenCapture:
    """Handles screen capture operations"""

    def __init__(self):
        self.sct = None
        if HAS_MSS:
            try:
                self.sct = mss.mss()
            except Exception as e:
                Logger.warning(f"Failed to initialize mss: {e}")
                self.sct = None

    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """
        Capture screenshot

        Args:
            region: Optional (x, y, width, height) tuple for specific region

        Returns:
            Screenshot as numpy array (RGB) or None if failed
        """
        # Try pyautogui first (more reliable on Linux)
        if HAS_PYAUTOGUI:
            try:
                if region:
                    x, y, width, height = region
                    screenshot = pyautogui.screenshot(region=(x, y, width, height))
                else:
                    screenshot = pyautogui.screenshot()

                img_array = np.array(screenshot)
                Logger.debug(f"Screenshot captured with pyautogui: {img_array.shape}")
                return img_array

            except Exception as e:
                Logger.warning(f"pyautogui capture failed: {e}, trying mss fallback")

        # Fallback to mss
        if self.sct:
            try:
                if region:
                    x, y, width, height = region
                    monitor = {
                        "top": y,
                        "left": x,
                        "width": width,
                        "height": height
                    }
                else:
                    # Capture primary monitor
                    monitor = self.sct.monitors[1]

                # Capture screenshot
                screenshot = self.sct.grab(monitor)

                # Convert to PIL Image then to numpy array
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                img_array = np.array(img)

                Logger.debug(f"Screenshot captured with mss: {img_array.shape}")
                return img_array

            except Exception as e:
                Logger.exception(f"mss capture also failed: {e}")
                return None

        Logger.error("No screenshot library available")
        return None

    def capture_and_save(self, filepath: str, region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """
        Capture screenshot and save to file

        Args:
            filepath: Path to save screenshot
            region: Optional (x, y, width, height) tuple

        Returns:
            True if successful, False otherwise
        """
        try:
            img_array = self.capture_screen(region)
            if img_array is None:
                return False

            # Convert to PIL Image and save
            img = Image.fromarray(img_array)
            img.save(filepath)

            Logger.info(f"Screenshot saved to: {filepath}")
            return True

        except Exception as e:
            Logger.exception(f"Error saving screenshot: {e}")
            return False

    def get_monitor_info(self):
        """Get information about available monitors"""
        monitors = self.sct.monitors
        Logger.info(f"Available monitors: {len(monitors) - 1}")  # -1 because monitors[0] is all monitors combined
        return monitors
