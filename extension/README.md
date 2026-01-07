# Dannazione di Providenza - Browser Extension

An alive agent integrated browser extension for real-time language assistance and intelligence.

## Features

- 🧠 **Alive Agent Architecture** - Intelligent assistant actively monitoring and responding
- 🔌 **WebSocket Connection** - Real-time bidirectional communication with agent backend
- 📸 **Screen Capture** - Instant OCR processing with global hotkeys
- 🔤 **Multi-Engine OCR** - Support for Tesseract, EasyOCR, and PaddleOCR
- 🌐 **Translation Services** - Google Translate, DeepL, and local models
- 🤖 **Local LLM Integration** - Privacy-first AI with Ollama
- 🎨 **Modern UI** - Non-intrusive overlay with gradient design

## Quick Start

### 1. Install Dependencies

```bash
make install
```

### 2. Build Extension

```bash
make build
```

This will:
- Prompt you to select environment (LOCAL/DEV/PROD)
- Run linting
- Build the extension
- Package it as a ZIP file in `extension_build/`

### 3. Load in Firefox

#### Development:
```bash
make firefox-dev
```

#### Manual Installation:
1. Open Firefox
2. Go to `about:debugging#/runtime/this-firefox`
3. Click "Load Temporary Add-on"
4. Navigate to `extension_build/extension_unpacked/` and select `manifest.json`

## Development

### Watch Mode
```bash
make watch
```

### Development Server
```bash
make dev
```

### Linting
```bash
make lint
```

### Format Code
```bash
make format
```

## Project Structure

```
extension/
├── src/
│   ├── background/        # Service worker
│   │   └── index.ts       # Agent manager, message routing
│   ├── content/           # Content scripts
│   │   ├── agentBridge.ts # Agent overlay and page integration
│   │   └── agentBridge.css
│   ├── popup/             # Extension popup UI
│   │   ├── index.tsx      # Main popup
│   │   ├── options.tsx    # Options page
│   │   └── popup.css
│   ├── lib/               # Shared libraries
│   ├── shared/            # Shared utilities
│   ├── config.ts          # Configuration
│   └── manifest.template.json
├── public/
│   └── images/            # Extension icons
├── scripts/               # Build scripts
├── dist/                  # Build output
├── extension_build/       # Packaged extension
├── Makefile
├── vite.config.ts
├── package.json
└── tsconfig.json
```

## Configuration

### Environment Selection

During build, you'll be prompted to select:
- **LOCAL** (0): `ws://localhost:8765`
- **DEV** (1): `wss://dev.providenza.ai`
- **PROD** (2): `wss://providenza.ai`

This is configured in `src/config.ts`.

### Agent Backend

The extension connects to a WebSocket server for the alive agent. Ensure your backend is running:

```bash
# In the main project directory
python main.py
```

## Hotkeys

- **Ctrl+Shift+S** - Capture screen for OCR
- **Ctrl+Shift+A** - Toggle agent overlay
- **Ctrl+Shift+T** - Quick translate selected text

## Build Targets

```bash
make help              # Show all available targets
make install           # Install dependencies
make clean             # Remove build artifacts
make quick-build       # Fast build without lint
make build             # Standard build with linting
make production        # Production build with analysis
make analyze           # Bundle analysis
make firefox           # Run in Firefox
make firefox-dev       # Run in Firefox Developer Edition
```

## Technologies

- **TypeScript** - Type-safe development
- **React** - UI components
- **Vite** - Fast build tool
- **WebExtension API** - Cross-browser compatibility
- **WebSocket** - Real-time agent communication
- **Zustand** - State management

## Browser Support

- Firefox 109.0+
- (Chrome/Edge support coming soon)

## License

MIT

## Agent Connection

The extension communicates with the Dannazione di Providenza agent backend via WebSocket:

1. **Background Service Worker** manages WebSocket connection
2. **Content Script** injects overlay into web pages
3. **Popup** provides quick access to agent features
4. **Options Page** allows configuration

### Message Flow

```
Web Page → Content Script → Background Worker → WebSocket → Agent Backend
                ↓                                              ↓
              Overlay ← Background Worker ← WebSocket ← Agent Backend
```
