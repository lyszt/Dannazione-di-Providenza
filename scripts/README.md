# Mesly Scripts

## Installation Script

### Usage

From the project root directory, run:

```bash
./scripts/install_dependencies.sh
```

### What it does

1. **Detects your package manager** (pacman, apt, dnf, zypper)
2. **Installs system dependencies:**
   - Python and pip
   - Tkinter (required for pyautogui)
   - Screenshot tools (gnome-screenshot, scrot)
   - PyQt5
   - Tesseract OCR with language packs (English, Japanese)
   - Build tools (for compiling Python packages)
3. **Installs Ollama** (if not already installed)

**Note:** This script does NOT install Python dependencies from requirements.txt.
Install those manually with your preferred method (pip, poetry, etc.) or bundle them when creating a binary.

### Supported Distributions

- **Arch Linux / Manjaro** (pacman)
- **Debian / Ubuntu** (apt)
- **Fedora** (dnf)
- **openSUSE** (zypper)

### Manual Installation

If the script doesn't work for your distribution, install these packages manually:

#### For Arch Linux / Manjaro
```bash
sudo pacman -S python python-pip tk gnome-screenshot scrot qt5-base tesseract tesseract-data-eng tesseract-data-jpn
pip install --user -r requirements.txt
```

#### For Debian / Ubuntu
```bash
sudo apt install python3 python3-pip python3-tk gnome-screenshot scrot python3-pyqt5 tesseract-ocr tesseract-ocr-eng tesseract-ocr-jpn
pip3 install --user -r requirements.txt
```

#### For Fedora
```bash
sudo dnf install python3 python3-pip python3-tkinter gnome-screenshot scrot python3-qt5 tesseract tesseract-langpack-eng tesseract-langpack-jpn
pip3 install --user -r requirements.txt
```

### Troubleshooting

**pyautogui screenshot error:**
- Make sure `gnome-screenshot` or `scrot` is installed
- Install tk: `sudo pacman -S tk` (Arch) or `sudo apt install python3-tk` (Ubuntu)

**Ollama not found:**
- Install manually: `curl -fsSL https://ollama.com/install.sh | sh`

**Permission denied:**
- Make script executable: `chmod +x scripts/install_dependencies.sh`
