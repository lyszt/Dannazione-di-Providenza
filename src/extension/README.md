# Dannazione - Browser Extension

Alive agent integrated browser extension built with Lit for real-time language assistance and intelligence.

## Features

- 🧠 **Alive Agent Architecture** - Real-time WebSocket connection to agent backend
- 📸 **Screen Capture** - OCR processing with global hotkeys
- 🌐 **Translation** - Instant translation of selected text
- 🤖 **Smart Agent** - Context-aware assistance
- ⚡ **Lit Components** - Fast, lightweight web components
- 🎨 **Modern UI** - Clean, gradient-themed interface

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
- Build the extension
- Package it as a ZIP file in `extension_build/`

### 3. Load in Firefox

#### Development:
```bash
make firefox
```

#### Manual Installation:
1. Open Firefox
2. Go to `about:debugging#/runtime/this-firefox`
3. Click "Load Temporary Add-on"
4. Navigate to `extension_build/extension_unpacked/` and select `manifest.json`

## Development

### Development Server
```bash
make dev
```

### Quick Build
```bash
make quick-build
```

## Project Structure

```
extension/
├── src/
│   ├── background.js          # Service worker, WebSocket agent connection
│   ├── content.js             # Content script for web pages
│   ├── popup.js               # Popup UI (Lit component)
│   ├── index.js              # Dynamic configuration
│   └── manifest.template.json # Manifest template
├── public/                    # Static assets
├── popup.html                 # Popup entry point
├── Makefile                   # Build system
├── vite.index.js             # Vite configuration
└── package.json
```

## Configuration

### Environment Selection

During build, select environment:
- **LOCAL** (0): `ws://localhost:8765`
- **DEV** (1): `ws://localhost:8766`
- **PROD** (2): `ws://localhost:8767`

Configuration is in `src/index.js`.

### Agent Backend

The extension connects via WebSocket. Start the agent backend:

```bash
cd ../..
python main.py
```

## Hotkeys

- **Ctrl+Shift+S** - Capture screen for OCR
- **Ctrl+Shift+A** - Toggle agent overlay

## Build Targets

```bash
make help              # Show all available targets
make install           # Install dependencies
make clean             # Remove build artifacts
make quick-build       # Fast build
make build             # Standard build with packaging
make production        # Production build
make firefox           # Run in Firefox
```

## Technologies

- **Lit** - Fast, lightweight web components
- **Vite** - Lightning-fast build tool
- **WebSocket** - Real-time agent communication
- **WebExtension API** - Firefox extension APIs

## Browser Support

- Firefox 109.0+

## Author

lyszt

## License

MIT
