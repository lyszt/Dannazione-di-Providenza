from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from threading import Thread
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from ..utils import Logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


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

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        model_name = "tencent/HY-MT1.5-7B"
        try:
            self.translation_pipeline = pipeline("translation", model=model_name)
        except Exception as e:
            Logger.error(f"Failed to load translation model '{model_name}': {e}")
            self.translation_pipeline = None

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
            return JSONResponse(content={"status": "selection updated"}, media_type="application/json")

        @self.app.post("/translate")
        async def translate_text(request: TranslateRequest):
            """Translate text using a local Hugging Face model"""
            if not self.translation_pipeline:
                return {
                    "translation": "[Translation error: Translation model not loaded]",
                    "error": "Model not available"
                }

            try:
                source = request.from_lang if request.from_lang != "auto" else "en"
                target = request.to_lang

                # Perform translation using the local model
                translated = self.translation_pipeline(request.text, src_lang=source, tgt_lang=target)

                Logger.info(f"Translation: '{request.text[:50]}...' -> '{translated[0]['translation_text'][:50]}...'")

                return {
                    "translation": translated[0]['translation_text'],
                    "from": source,
                    "to": target
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
