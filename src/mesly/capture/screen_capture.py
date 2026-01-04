"""
Screen capture functionality - Universal Linux Support
"""
import numpy as np
import subprocess
import os
from PIL import Image
from typing import Optional, Tuple
from ..utils import Logger

# Check for libraries
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
        Universal capture chain: MSS -> PyAutoGUI -> Native Wayland CLI
        """

        # 1. Try MSS
        if self.sct:
            try:
                if region:
                    monitor = {"top": region[1], "left": region[0], "width": region[2], "height": region[3]}
                else:
                    monitor = self.sct.monitors[1]

                sct_img = self.sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
                return np.array(img)
            except Exception:
                pass  #

        if HAS_PYAUTOGUI:
            try:
                if region:
                    screenshot = pyautogui.screenshot(region=region)
                else:
                    screenshot = pyautogui.screenshot()
                return np.array(screenshot)
            except Exception:
                pass

        return self._capture_wayland_cli(region)

    def _capture_wayland_cli(self, region: Optional[Tuple[int, int, int, int]]) -> Optional[np.ndarray]:
        """
        Detects the Desktop Environment and uses the native CLI tool.
        Captures full screen and crops in memory to avoid interactive prompts.
        """
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").upper()
        temp_path = "/tmp/mesly_universal_capture.png"

        # Define the command based on DE
        cmd = []
        if "KDE" in desktop:
            # Spectacle: -b (background), -n (non-notify), -o (output)
            cmd = ["spectacle", "-b", "-n", "-o", temp_path]
        elif "GNOME" in desktop:
            # Gnome-screenshot: -f (file)
            cmd = ["gnome-screenshot", "-f", temp_path]
        elif "SWAY" in desktop or "HYPRLAND" in desktop:
            # Grim: Standard for wlroots
            cmd = ["grim", temp_path]
        else:
            # Fallback for generic/unknown Wayland (try grim as it's common)
            Logger.warning(f"Unknown Desktop '{desktop}', trying grim...")
            cmd = ["grim", temp_path]

        try:
            # Cleanup old file
            if os.path.exists(temp_path):
                os.remove(temp_path)

            # Run the command silently
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

            if os.path.exists(temp_path):
                with Image.open(temp_path) as img:
                    img = img.convert("RGB")

                    # Handle cropping in Python (Bypasses UI selectors)
                    if region:
                        x, y, w, h = region
                        img = img.crop((x, y, x + w, y + h))

                    img_array = np.array(img)

                # Cleanup
                os.remove(temp_path)
                Logger.debug(f"Captured with Native CLI ({cmd[0]}): {img_array.shape}")
                return img_array

        except subprocess.CalledProcessError:
            Logger.error(f"Native capture tool '{cmd[0]}' failed. Is it installed?")
        except Exception as e:
            Logger.error(f"Unexpected capture error: {e}")

        return None

    def capture_and_save(self, filepath: str, region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        img_array = self.capture_screen(region)
        if img_array is not None:
            Image.fromarray(img_array).save(filepath)
            return True
        return False

    def get_monitor_info(self):
        if self.sct:
            return self.sct.monitors
        return []