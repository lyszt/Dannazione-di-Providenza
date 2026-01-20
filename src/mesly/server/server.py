from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from threading import Thread
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from ..utils import Logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from concurrent.futures import ThreadPoolExecutor
import time
from collections import defaultdict


def trim_after_last_period(s: str) -> str:
    """Return the input trimmed to the last full sentence (through the final period).
    If no period is found, return the original stripped string.
    """
    if s is None:
        return s
    if not isinstance(s, str):
        s = str(s)
    s = s.strip()
    last_dot = s.rfind('.')
    if last_dot == -1:
        return s
    return s[: last_dot + 1].strip()

class TranslateRequest(BaseModel):
    text: str
    from_lang: str = "auto"
    to_lang: str = "en"


class PromptRequest(BaseModel):
    prompt: str
    body: dict = {}


class ChatRequest(BaseModel):
    prompt: str
    body: dict = {}


class ContextRequest(BaseModel):
    url: str
    title: str
    html: str
    type: str = "default"

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

        self.translation_pipeline = None
        self.translation_model_loading = True
        self.translation_model_error = None
        self.translation_cache = {}  # Cache translations
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._initialize_translation_model()

        self._setup_routes()
        self._thread = None

    def _initialize_translation_model(self):
        def load_model():
            model_name = "Helsinki-NLP/opus-mt-mul-en"
            try:
                Logger.info(f"Loading translation model '{model_name}'...")
                self.translation_pipeline = pipeline("translation", model=model_name, device_map="auto")
                self.translation_model_loading = False
                Logger.info(f"Translation model '{model_name}' loaded successfully.")
            except Exception as e:
                self.translation_model_loading = False
                self.translation_model_error = str(e)
                Logger.error(f"Failed to load translation model '{model_name}': {e}")

        self._executor.submit(load_model)

    def _setup_routes(self):
        @self.app.get("/")
        async def root():
            return {"message": "Dannazione di Providenza Server is running."}

        @self.app.post("/context")
        async def context(request: ContextRequest):
            # Push context to Agent's browser context
            if self.agent:
                self.agent.knowledge_base.browser_context.push(request.url, request.title, request.html)

                # Save to long-term memory
                if self.agent.long_term_memory:
                    try:
                        self.agent.long_term_memory.browser_history.save(
                            url=request.url,
                            title=request.title,
                            body=request.html
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
        def translate_text(request: TranslateRequest):
            """Translate text using Helsinki-NLP translation model"""
            # Rate limiting with caching: return cached translation for duplicate requests
            current_time = time.time()
            cache_key = f"{request.text[:100]}_{request.from_lang}_{request.to_lang}"

            self.translation_cache = {
                k: v for k, v in self.translation_cache.items()
                if current_time - v['timestamp'] < 10
            }

            if cache_key in self.translation_cache:
                cached = self.translation_cache[cache_key]
                Logger.info(f"Returning cached translation for: '{request.text[:50]}...'")
                return {
                    "translation": cached['translation'],
                    "from": request.from_lang,
                    "to": request.to_lang,
                    "cached": True
                }

            if self.translation_model_loading:
                return {
                    "translation": "[Translation model is still loading... Please wait]",
                    "error": "Model loading"
                }

            if self.translation_model_error:
                return {
                    "translation": f"[Translation model failed to load: {self.translation_model_error}]",
                    "error": self.translation_model_error
                }

            if not self.translation_pipeline:
                return {
                    "translation": "[Translation error: Translation model not available]",
                    "error": "Model not available"
                }

            try:
                # Perform translation
                result = self.translation_pipeline(request.text)
                translation = result[0]['translation_text']

                # Cache the result
                self.translation_cache[cache_key] = {
                    'translation': translation,
                    'timestamp': current_time
                }

                Logger.info(f"Translation: '{request.text[:50]}...' -> '{translation[:50]}...'")

                return {
                    "translation": translation,
                    "from": request.from_lang,
                    "to": request.to_lang
                }
            except Exception as e:
                Logger.error(f"Translation failed: {e}")
                return {
                    "translation": f"[Translation error: {str(e)}]",
                    "error": str(e)
                }

        @self.app.post("/chat")
        async def send_chat(request: ChatRequest):
            try:
                if not self.agent:
                    return {"reply": "Agent not initialized", "status": "error"}

                if not self.agent.is_ready():
                    return {"reply": "AI client not available. Please check your configuration.", "status": "error"}

                raw_html = None
                page_obj = None
                if isinstance(request.body, dict):
                    page_obj = request.body.get('page')
                    if isinstance(page_obj, dict):
                        Logger.info(f"Server /chat: received page keys={list(page_obj.keys())}")
                        try_html = page_obj.get('html') or page_obj.get('body')
                        if try_html:
                            Logger.info(f"Server /chat: page.url={page_obj.get('url')} html_length={len(try_html)}")
                        raw_html = try_html
                elif isinstance(request.body, (str, bytes)):
                    raw_html = request.body

                if raw_html:
                    soup = BeautifulSoup(raw_html, 'lxml')


                    raw_text = soup.get_text()
                    # normalize whitespace and trim
                    body_text = ' '.join(raw_text.split())
                    Logger.info(f"Server /chat: parsed body_text length={len(body_text)} snippet={body_text[:200]}")
                else:
                    Logger.info("Server /chat: no inline HTML provided in request.body.page")
                    body_text = ''

                # Get context text from selected text if available
                context_text = None
                if hasattr(self.agent, 'knowledge_base') and hasattr(self.agent.knowledge_base, 'browser_context'):
                    ctx = self.agent.knowledge_base.browser_context
                    context_text = f" USER IS VIEWING: {body_text} --- USER SELECTED TEXT: {ctx.selected_text if ctx.selected_text else ""}"
                else:
                    context_text = f" USER IS VIEWING: {body_text}"

                # Use the actual agent method with browser context enabled
                response = self.agent.process_user_question(
                    question=request.prompt,
                    context_text=context_text,
                    use_browser_context=True,
                    stream_callback=None
                )



                if response:
                    reply_text = trim_after_last_period(response)
                    return {"reply": reply_text, "status": "success"}
                else:
                    return {"reply": "Failed to generate response", "status": "error"}

            except Exception as e:
                Logger.error(f"Chat error: {e}")
                return {"reply": f"Error: {str(e)}", "status": "error"}

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
