# Mesly

OCR-based language learning tool for gaming

## Quick Start

### 1. Install Dependencies

Run the installation script:

```bash
./scripts/install_dependencies.sh
```

Or see `scripts/README.md` for manual installation instructions.

### 2. Run Mesly

```bash
python main.py
```

### 3. Use Hotkeys

- **Ctrl+Shift+T** - Capture screenshot

## Features

- 📸 Screenshot capture with global hotkeys
- 🔤 OCR text recognition (Tesseract, EasyOCR, PaddleOCR)
- 🌐 Translation services (Google Translate, DeepL)
- 🤖 Local LLM support (Ollama with Phi-3.5)
- 🎨 PyQt5 overlay interface

## Requirements

- Python 3.8+
- Linux (X11)
- See `requirements.txt` for Python dependencies

## Configuration

Config file: `config/config.yaml`

Edit to configure:
- OCR engines and languages
- Translation services
- Local LLM models
- Hotkeys and shortcuts

## Project Structure

```
Mesly/
├── src/mesly/          # Main package
│   ├── capture/        # Screenshot capture
│   ├── config/         # Configuration management
│   ├── llm/           # LLM clients (cloud & local)
│   ├── ocr/           # OCR engines
│   ├── overlay/       # UI overlay
│   ├── translation/   # Translation services
│   ├── utils/         # Utilities (logging, hotkeys)
│   └── window/        # PyQt5 windows
├── scripts/           # Installation scripts
├── config/            # Configuration files
├── data/             # Screenshots and data
└── logs/             # Log files
```

## License

MIT
