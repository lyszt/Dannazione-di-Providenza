"""
Model setup and initialization utilities
"""

import subprocess
import time
import atexit
import signal
import sys
from typing import Optional
from multiprocessing import Process
from ..utils import Logger


class ModelSetup:
    """Handles model downloading and setup for local LLMs"""

    _ollama_process: Optional[Process] = None
    _ollama_subprocess: Optional[subprocess.Popen] = None

    @classmethod
    def _cleanup_ollama(cls):
        """Cleanup Ollama server process"""
        if cls._ollama_subprocess:
            try:
                Logger.info("Shutting down Ollama server...")
                cls._ollama_subprocess.terminate()
                cls._ollama_subprocess.wait(timeout=5)
                Logger.info("Ollama server stopped")
            except subprocess.TimeoutExpired:
                Logger.warning("Ollama server did not stop gracefully, forcing...")
                cls._ollama_subprocess.kill()
            except Exception as e:
                Logger.error(f"Error stopping Ollama server: {e}")

    @classmethod
    def _is_ollama_running(cls) -> bool:
        """Check if Ollama server is already running"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception as e:
            Logger.error(f"Error checking if Ollama server is running: {e}")
            return False

    @classmethod
    def start_ollama_server(cls) -> bool:
        """
        Start Ollama server in background

        Returns:
            True if server started successfully, False otherwise
        """
        try:
            # Check if already running
            if cls._is_ollama_running():
                Logger.info("Ollama server is already running")
                return True

            Logger.info("Starting Ollama server...")

            # Start ollama serve as subprocess
            cls._ollama_subprocess = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            # Register cleanup handlers
            atexit.register(cls._cleanup_ollama)
            signal.signal(signal.SIGINT, lambda s, f: cls._cleanup_ollama() or sys.exit(0))
            signal.signal(signal.SIGTERM, lambda s, f: cls._cleanup_ollama() or sys.exit(0))

            # Wait for server to be ready
            Logger.info("Waiting for Ollama server to be ready...")
            max_retries = 10
            for i in range(max_retries):
                time.sleep(1)
                if cls._is_ollama_running():
                    Logger.info("Ollama server started successfully")
                    return True

            Logger.error("Ollama server failed to start within timeout")
            return False

        except FileNotFoundError:
            Logger.warning("Ollama command not found. Install from https://ollama.com")
            return False
        except Exception as e:
            Logger.exception(f"Error starting Ollama server: {e}")
            return False

    @classmethod
    def ensure_ollama_model(cls, model_name: str = "phi3.5") -> bool:
        """
        Ensure Ollama model is downloaded and ready

        Args:
            model_name: Ollama model name (default: phi3.5 - Phi-3.5 Mini 3.8B)

        Returns:
            True if model is ready, False otherwise
        """
        try:
            # Check if ollama is installed
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                Logger.warning("Ollama is not installed. Install from https://ollama.com")
                return False

            Logger.info(f"Checking if Ollama model '{model_name}' is available...")

            # Check if model exists
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if model_name.split(":")[0] in result.stdout:
                Logger.info(f"Ollama model '{model_name}' is already available")
                return True

            # Download model
            Logger.info(f"Downloading Ollama model '{model_name}'... This may take a while.")
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout for download
            )

            if result.returncode == 0:
                Logger.info(f"Successfully downloaded Ollama model '{model_name}'")
                return True
            else:
                Logger.error(f"Failed to download Ollama model: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            Logger.error("Ollama command timed out")
            return False
        except FileNotFoundError:
            Logger.warning("Ollama command not found. Install from https://ollama.com")
            return False
        except Exception as e:
            Logger.exception(f"Error setting up Ollama model: {e}")
            return False

    @classmethod
    def setup_local_models(cls) -> None:
        """Setup all local models on startup"""
        Logger.info("Setting up local models...")

        # Start Ollama server first
        if not cls.start_ollama_server():
            Logger.error("Failed to start Ollama server. Local models will not be available.")
            return

        # Setup Ollama Phi-3.5 Mini (3.8B)
        if cls.ensure_ollama_model("phi3.5"):
            Logger.info("Local model setup completed successfully")
        else:
            Logger.warning("Local model setup encountered issues. Check logs for details.")

    @classmethod
    def stop_ollama_server(cls) -> None:
        """Manually stop Ollama server"""
        cls._cleanup_ollama()
