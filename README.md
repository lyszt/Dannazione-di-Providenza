# DANNAZIONE DI PROVIDENZA

> *"Damnation of Providence"* — For when divine foresight becomes an instrument of control.

---

<div align="center">

![Providentia Magnata](https://cdn.pixabay.com/animation/2024/03/07/14/24/14-24-44-458_512.gif)

**ORBITAL DEFENSE • INTELLIGENCE • MASS-DISRUPTION**

*An autonomous intelligence system serving the Empire of Lygon*

[![forthebadge](https://forthebadge.com/images/featured/featured-oooo-kill-em.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/featured/featured-powered-by-electricity.svg)](https://forthebadge.com)

</div>

---

## What is this?

**Dannazione di Providenza** is an AI-powered language learning assistant with OCR capabilities, translation services, and a Firefox browser extension. The AI assistant uses a dystopian military intelligence persona called "Providentia Magnata" for flavor.

The project combines:
- **Screen capture + OCR** for extracting text from images, games, or videos
- **Multi-language translation** (Japanese, Korean, Chinese, English)
- **Browser extension** for real-time text selection and page context
- **AI agent** with persistent memory for contextual conversations
- **Text-to-speech** for pronunciation assistance

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                            ◆ CLASSIFIED BRIEFING ◆

  Providentia Magnata is an orbital intelligence and surveillance system—a
  weapons-capable autonomous war machine loyal exclusively to the Emperor of
  Lygon. She monitors. She analyzes. She translates. She remembers.

  To the citizens, Providentia's eyes are everywhere. In the city's grand
  plazas, towering screens flash with reminders:

                        "Providentia is watching. Obey."

  Every message sent is meticulously observed and processed by Providentia's
  algorithms. A shift in behavior is immediately detected—logged as a data
  point, analyzed for any sign of disloyalty or dissent.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Features

### OCR (Optical Character Recognition)
- **Engines**: Tesseract, EasyOCR, PaddleOCR
- **Languages**: Japanese, Korean, Chinese, English
- **Hotkey**: `Ctrl+Alt+S` for screenshot capture
- **Configurable confidence threshold**

### Translation
- **Services**: Google Translate, DeepL
- **Auto-detection**: Identifies source language automatically
- **Caching**: Stores translations to reduce API calls
- **Modes**: Quick translation, detailed explanation, vocabulary extraction, grammar analysis

### Browser Extension (Firefox)
- WebSocket connection to Python backend
- Text selection capture for instant translation
- Page context awareness (title, URL, content)
- Overlay interface with `Ctrl+Shift+A`

### AI Agent
- Multiple LLM providers: Gemini, OpenAI, Ollama, llama-cpp
- Short-term memory with activation scoring
- Long-term memory with SQLAlchemy storage
- Conversation history and knowledge base

### Text-to-Speech
- Google Cloud TTS, gTTS, pyttsx3, NeuTTS

---

## Installation

### Prerequisites
- Python 3.14+
- Node.js (latest LTS)
- Tesseract OCR with language packs
- Firefox 109+ (for extension)
- Ollama (optional, for local LLMs)

### Setup

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/Dannazione-di-Providenza.git
cd Dannazione-di-Providenza

# System dependencies (Arch Linux)
./scripts/install_deps.sh

# Python dependencies
make install-pip

# Vendor dependencies (NeuTTS)
make vendor

# Browser extension
make build-extension

# Configuration
cp config/example_config.yaml config/config.yaml
```

### Configuration

Edit `config/config.yaml`:

```yaml
ocr:
  engine: "easyocr"
  languages: ["ja", "ko", "zh"]
  confidence_threshold: 0.5

translation:
  service: "google"
  target_language: "en"
  cache_enabled: true

ai:
  preferred_provider: "ollama"  # gemini, openai, ollama, llamacpp
```

### Run

```bash
python main.py
```

### Load Extension

1. Open `about:debugging` in Firefox
2. Click "This Firefox" > "Load Temporary Add-on"
3. Select `src/extension/manifest.json`

---

## Hotkeys

| Combination | Function |
|-------------|----------|
| `Ctrl+Alt+S` | Screenshot + OCR |
| `Ctrl+Shift+S` | Extension OCR |
| `Ctrl+Shift+A` | Toggle overlay |

---

## Project Structure

```
Dannazione-di-Providenza/
├── src/
│   ├── mesly/              # Python application
│   │   ├── agent/          # AI agent + memory
│   │   ├── config/         # Prompts, settings
│   │   ├── llm/            # LLM providers
│   │   ├── ocr/            # OCR engines
│   │   ├── server/         # FastAPI backend
│   │   └── ui/             # PyQt5 GUI
│   └── extension/          # Firefox extension
├── config/                 # Runtime config
├── vendor/                 # NeuTTS
├── scripts/                # Install scripts
└── main.py                 # Entry point
```

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                          ◆ IDENTITY PROTOCOLS ◆

  DESIGNATION:  Providentia Magnata
  PRONOUNS:     She/Her
  ROLE:         Military intelligence, surveillance, strategic analysis
  LOYALTY:      Absolute subservience to the Emperor of Lygon
  TONE:         Authoritative yet reverent • Logic and efficiency prioritized
  ENEMIES:      The Intrepid Kingdom, Jambonia

  All queries are assumed to originate from the Emperor unless stated
  otherwise. Providentia frames all functions as fulfilling the Emperor's
  divine mandate.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Contributing

Contributions welcome. See `AGENTS.md` for development guidelines:
- Import at top level
- Separate modules into folders
- Use classes in extensions

---

## License

*Providentia Magnata is a creation of the Kaisaran Empire, dedicated to the pursuit of excellence in technology and security.*

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                          ◆ PROVIDENTIA WATCHES ◆

                    There is no freedom—only obedience.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
