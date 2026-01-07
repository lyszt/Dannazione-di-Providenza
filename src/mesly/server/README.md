# Dannazione di Providenza API

FastAPI server that provides programmatic access to the language learning assistant.

## Base URL
```
http://127.0.0.1:8000
```

## Endpoints

### `GET /`
Health check endpoint.

**Response:**
```json
{
  "message": "Dannazione di Providenza Server is running."
}
```

---

### `GET /health`
Detailed health status including AI availability.

**Response:**
```json
{
  "status": "healthy",
  "ai_available": true,
  "timestamp": "2026-01-07T23:00:00.000000"
}
```

---

### `GET /config`
Get current configuration (sanitized, no API keys).

**Response:**
```json
{
  "ai_provider": "gemini",
  "languages": {
    "native": "en",
    "target": "de"
  },
  "tts_enabled": true
}
```

---

### `POST /ask`
Ask the AI a question, optionally with OCR from an image.

**Request Body:**
```json
{
  "question": "What does 'Guten Morgen' mean?",
  "image_path": "data/screenshots/screenshot_20260107_153145.png"  // optional
}
```

**Response:**
```json
{
  "answer": "Guten Morgen means 'Good morning' in German...",
  "ocr_used": false,
  "timestamp": "2026-01-07T23:00:00.000000"
}
```

**Error Responses:**
- `503` - AI client not available
- `404` - Image not found (if image_path provided)
- `500` - Internal server error

---

### `POST /screenshot`
Capture a full-screen screenshot.

**Response:**
```json
{
  "success": true,
  "filepath": "data/screenshots/screenshot_20260107_230000.png",
  "timestamp": "2026-01-07T23:00:00.000000"
}
```

**Error Responses:**
- `503` - Screen capture not available
- `500` - Screenshot capture failed

---

## Testing

Run the test script while the app is running:

```bash
python test_api.py
```

## Integration Examples

### Browser Extension
```javascript
// Ask a question
fetch('http://127.0.0.1:8000/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: 'What is this word?' })
})
.then(r => r.json())
.then(data => console.log(data.answer));
```

### Python Script
```python
import requests

# Take screenshot and ask about it
screenshot = requests.post('http://127.0.0.1:8000/screenshot').json()
response = requests.post('http://127.0.0.1:8000/ask', json={
    'question': 'Translate this text',
    'image_path': screenshot['filepath']
}).json()
print(response['answer'])
```

### Command Line (curl)
```bash
# Health check
curl http://127.0.0.1:8000/health

# Ask a question
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What does Vorrangstellung mean?"}'

# Take screenshot
curl -X POST http://127.0.0.1:8000/screenshot
```

## Security Notes

- The API currently runs on localhost only (127.0.0.1)
- No authentication is implemented (local use only)
- API keys and sensitive config are not exposed through the API
- For external access, implement proper authentication and use HTTPS

