import platform
import subprocess
import shutil
import re
from typing import List, Optional, Tuple
from ..utils import Logger

# Only import Windows libs if we are on Windows
if platform.system() == "Windows":
    try:
        import pygetwindow as gw
    except ImportError:
        Logger.warning("pygetwindow not installed. Window selection will fail on Windows.")


class WindowSelector:
    def __init__(self):
        self.system = platform.system()

        # Resolve paths once to avoid repetitive lookups and path issues
        self.kdotool_path = shutil.which("kdotool")
        self.wmctrl_path = shutil.which("wmctrl")

        # Booleans for easy checks
        self.has_kdotool = self.kdotool_path is not None
        self.has_wmctrl = self.wmctrl_path is not None

        if self.system == "Linux" and not self.has_kdotool:
            Logger.warning("kdotool not found. KDE window tracking will fail.")

    def get_window_list(self) -> List[str]:
        """Returns a list of window titles to populate the UI"""
        titles = []

        if self.system == "Windows":
            try:
                titles = [w.title for w in gw.getAllWindows() if w.title]
            except Exception as e:
                Logger.error(f"Windows window list failed: {e}")

        elif self.system == "Linux":
            # --- STRATEGY 1: KDE Wayland (kdotool) ---
            if self.has_kdotool:
                try:
                    # Get all window IDs
                    output = subprocess.check_output(
                        [self.kdotool_path, "search", "--all", "--name", ".*"],
                        text=True,
                        stderr=subprocess.DEVNULL
                    )

                    for wid in output.splitlines():
                        if not wid.strip(): continue
                        try:
                            # Get name for each ID
                            name = subprocess.check_output(
                                [self.kdotool_path, "getwindowname", wid],
                                text=True,
                                stderr=subprocess.DEVNULL
                            ).strip()

                            if name:
                                titles.append(name)
                        except subprocess.CalledProcessError:
                            continue
                except Exception as e:
                    Logger.error(f"kdotool search failed: {e}")

            # --- STRATEGY 2: X11 Fallback (wmctrl) ---
            elif self.has_wmctrl:
                try:
                    output = subprocess.check_output([self.wmctrl_path, "-l"], text=True)
                    # wmctrl output format: ID desktop machine TITLE...
                    for line in output.splitlines():
                        parts = line.split(maxsplit=3)
                        if len(parts) > 3:
                            titles.append(parts[3])
                except Exception:
                    pass

        return sorted(list(set(titles)))

    def get_window_geometry(self, window_title: str) -> Optional[Tuple[int, int, int, int]]:
        """
        Finds the (x, y, width, height) of the window dynamically.
        """
        if self.system == "Windows":
            try:
                wins = gw.getWindowsWithTitle(window_title)
                if wins:
                    w = wins[0]
                    # On Windows, we can easily check/restore minimized windows
                    if w.isMinimized:
                        w.restore()
                    return (w.left, w.top, w.width, w.height)
            except Exception:
                pass

        elif self.system == "Linux":
            # --- STRATEGY 1: KDE Wayland (kdotool) ---
            if self.has_kdotool:
                try:
                    # 1. Find ID (limit 1)
                    wid = subprocess.check_output(
                        [self.kdotool_path, "search", "--limit", "1", "--name", window_title],
                        text=True,
                        stderr=subprocess.DEVNULL
                    ).strip()

                    if not wid:
                        return None

                    # 2. Get Geometry
                    # Output example: "Window 123 is at 100,200 and is 800x600"
                    geo = subprocess.check_output(
                        [self.kdotool_path, "getwindowgeometry", wid],
                        text=True,
                        stderr=subprocess.DEVNULL
                    ).strip()

                    match = re.search(r"at (-?\d+),(-?\d+) and is (\d+)x(\d+)", geo)
                    if match:
                        return (
                            int(match.group(1)),  # x
                            int(match.group(2)),  # y
                            int(match.group(3)),  # width
                            int(match.group(4))  # height
                        )
                except Exception:
                    pass

            elif self.has_wmctrl:
                try:
                    output = subprocess.check_output([self.wmctrl_path, "-lG"], text=True)
                    for line in output.splitlines():
                        if window_title in line:
                            parts = line.split()
                            return (
                                int(parts[2]),  # x
                                int(parts[3]),  # y
                                int(parts[4]),  # w
                                int(parts[5])  # h
                            )
                except Exception:
                    pass

        return None

    def activate_window(self, window_title: str):
        """
        Forces the window to the front.
        Critical for Wayland to capture minimized windows.
        """
        if self.system == "Windows":
            try:
                win = gw.getWindowsWithTitle(window_title)[0]
                if win.isMinimized:
                    win.restore()
                win.activate()
            except:
                pass

        elif self.system == "Linux" and self.has_kdotool:
            try:
                wid = subprocess.check_output(
                    [self.kdotool_path, "search", "--limit", "1", "--name", window_title],
                    text=True
                ).strip()

                if wid:
                    subprocess.run(
                        [self.kdotool_path, "windowactivate", wid],
                        check=True,
                        stdout=subprocess.DEVNULL
                    )
            except Exception as e:
                Logger.warning(f"Failed to activate window '{window_title}': {e}")