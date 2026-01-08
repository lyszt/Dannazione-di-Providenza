from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from threading import Thread
from deep_translator import GoogleTranslator
from ..utils import Logger


class TranslateRequest(BaseModel):
    text: str
    from_lang: str = "auto"
    to_lang: str = "en"


class Server:
    def __init__(self, host="127.0.0.1", port=8000, agent=None, config=None, screen_capture=None):
        self.host = host
        self.port = port
        self.agent = agent
        self.config = config
        self.screen_capture = screen_capture
        self.app = FastAPI(title="Dannazione di Providenza API")
        self._setup_routes()
        self._thread = None

    def _setup_routes(self):
        @self.app.get("/")
        async def root():
            return {"message": "Dannazione di Providenza Server is running."}

        @self.app.post("/context")
        async def context(url, title, html_body):
            # Push context to Agent's browser context
            if self.agent:
                self.agent.knowledge_base.browser_context.push(url, title, html_body)

                # Save to long-term memory
                if self.agent.long_term_memory:
                    try:
                        self.agent.long_term_memory.browser_history.save(
                            url=url,
                            title=title,
                            body=html_body
                        )
                    except Exception as e:
                        Logger.error(f"Server: Failed to save browser history: {e}")

            return {"status": "context updated"}

        @self.app.post("/context/select")
        async def selection(data: dict):
            # Update selected text in browser context
            if self.agent and "text" in data:
                self.agent.knowledge_base.browser_context.selected_text = data["text"]
            return {"status": "selection updated"}

        @self.app.post("/translate")
        async def translate_text(request: TranslateRequest):
            """Translate text using deep-translator"""
            try:
                source = request.from_lang if request.from_lang != "auto" else "auto"

                translator = GoogleTranslator(source=source, target=request.to_lang)
                translated = translator.translate(request.text)

                Logger.info(f"Translation: '{request.text[:50]}...' -> '{translated[:50]}...'")

                return {
                    "translation": translated,
                    "from": source,
                    "to": request.to_lang
                }
            except Exception as e:
                Logger.error(f"Translation failed: {e}")
                return {
                    "translation": f"[Translation error: {str(e)}]",
                    "error": str(e)
                }

    def start(self):
        """Start the FastAPI server in a background thread"""
        if self._thread is not None and self._thread.is_alive():
            return  # Already running

        def run_server():
            uvicorn.run(
                self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )

        self._thread = Thread(target=run_server, daemon=True)
        self._thread.start()

    def is_running(self):
        """Check if the server thread is running"""
        return self._thread is not None and self._thread.is_alive()
