# DANNAZIONE DI PROVIDENZA

> *"Damnation of Providence"* — For when divine foresight becomes an instrument of control.

---

<img width="736" height="414" alt="image" src="https://github.com/user-attachments/assets/9600986f-47b9-41f8-979f-557508b6ede3" />

**LANGUAGE LEARNING • INTELLIGENCE • AGENTIC BROWSING PARTNER**

*An autonomous intelligence system serving the Empire of Lygon*

---

## What is this?

**Dannazione di Providenza** is an AI-powered language learning assistant with OCR capabilities, translation services, and a Firefox browser extension. 
> The AI assistant uses a dystopian military intelligence persona called "Providentia Magnata" for flavor. It helps add some character.

## Features

### 1. Translation
* **Engine:** Local **Helsinki-NLP (MarianMT)** models. No Google/DeepL API dependency.
* **Mechanism:** Direct DOM injection. Injects Shadow DOM tooltips.
* **Privacy:** Fully offline capable. Your reading habits never leave your machine.
* **Context:** Translation is aware of the full paragraph structure (captured via DOM), not just isolated words.

### 2. Live DOM Content Reading while you browse
* **Zero-Shot Awareness:** The agent knows exactly what you are looking at.
* **Sliding Window Memory:** Uses a `deque(maxlen=3)` structure to hold the last 3 visited pages in short-term memory, allowing for intent analysis.
* **Chat with Page:** Ask questions directly to the active tab: *"Is this news article biased?"* or *"Summarize the pricing table."*

### 3. Text-to-Speech technology
* **Engine:** Local **NeuTTS** (Neural Text-to-Speech).
* **Function:** Select text (or a person's name) and hear an instant audio briefing.
* **Use Case:** Quick intelligence gathering without breaking visual focus.

### 4. Security uses
* **Anti-Deception:** Scans the DOM for "Dark Patterns" (fake countdown timers, confusing unsubscribe buttons).
* **Trust Score:** Assigns a heuristic rating to pages based on content integrity and logical consistency.
* 
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

## ~ Potential Security Uses ~

*Current status: Conceptual / In Active R&D. These modules represent the ultimate goal of the "Cognitive Firewall."*

The Dannazione architecture allows for security measures that go beyond traditional blacklists. by analyzing the **semantic intent** of a webpage, Providentia can defend against threats that technically look "safe" but are psychologically malicious.

### 1. Narrative Verification (Live Disinformation Defense)
* **Concept:** Real-time cross-referencing of news articles against a trusted local vector database.
* **Goal:** A "Heads-Up Display" for truth in an era of post-truth media.

### 2. Synthetic Origin Detection (Anti-AI)
* **Concept:** Defense against the "Dead Internet Theory."
* **Goal:** Filter out the machine noise to find the remaining human signal.

### 3. Social Engineering Firewall (Scam Protection)
* **Concept:** Detecting *persuasion* rather than just malware.
* **Goal:** Preventing the user from falling for phishing sites that bypass standard URL filters.

### 4. Cognitive Filtering (Intelligent Ad-Blocking)
* **Concept:** Blocking "Native Advertising" that regex blockers miss.
* **Mechanism:** Using computer vision and semantic analysis to identify "Sponsored Content" disguised as legitimate journalism.
* **Action:** Instead of leaving a blank space, the Agent rewrites the DOM to remove the element entirely, seamlessly healing the layout.
* **Goal:** A purely informational browsing experience, devoid of corporate propaganda.

### 5. Active Camouflage (Tracker Poisoning)
* **Concept:** If you can't hide, create noise.
* **Mechanism:** The extension autonomously visits random websites in a background headless process, clicking random links to poison the data profile built by advertising trackers.
* **Goal:** Rendering the user's digital fingerprint useless to surveillance capitalism.
* 
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
