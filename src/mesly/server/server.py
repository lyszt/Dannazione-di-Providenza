from fastapi import FastAPI
import uvicorn
from threading import Thread


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
            return {"status": "context updated"}


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

