import os
import re
import base64
from PIL import Image
from gtts import gTTS
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QTextEdit, QScrollArea)
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from ..capture.stream_thread import ScreenShareThread
from ..llm import LocalLLMClientManager
from ..utils import Logger
from ..config.prompts import LanguageTutorPrompts, get_tutor_prompt
from ..config.config import ConfigTemplate

try:
    from google import genai
    from google.genai import types
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    from google.cloud import texttospeech
    HAS_CLOUD_TTS = True
except ImportError:
    HAS_CLOUD_TTS = False


def strip_markdown(text: str) -> str:
    """
    Remove markdown formatting from text.

    Args:
        text: Text with markdown formatting

    Returns:
        Plain text without markdown formatting
    """
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

    # Remove bold/italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text)  # Bold+italic
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)  # Italic
    text = re.sub(r'__(.+?)__', r'\1', text)  # Bold
    text = re.sub(r'_(.+?)_', r'\1', text)  # Italic

    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # Remove strikethrough
    text = re.sub(r'~~(.+?)~~', r'\1', text)

    # Remove horizontal rules
    text = re.sub(r'^[\-\*]{3,}$', '', text, flags=re.MULTILINE)

    # Remove list markers
    text = re.sub(r'^\s*[\*\-\+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

    # Remove blockquotes
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)

    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    return text


class AIGenerationThread(QThread):
    """Thread for running AI generation without blocking the GUI"""
    streaming = pyqtSignal(str)  # Emits partial chunks during streaming
    finished = pyqtSignal(str)  # Emits the complete AI response
    error = pyqtSignal(str)  # Emits error message

    def __init__(self, ai_client, prompt, system_prompt=None):
        super().__init__()
        self.ai_client = ai_client
        self.prompt = prompt
        self.system_prompt = system_prompt

    def run(self):
        """Run AI generation in background thread with streaming"""
        try:
            response = self.ai_client.generate(
                prompt=self.prompt,
                system_prompt=self.system_prompt,
                stream_callback=lambda chunk: self.streaming.emit(chunk)
            )
            if response:
                self.finished.emit(response)
            else:
                self.error.emit("AI returned empty response")
        except Exception as e:
            Logger.exception(f"Error in AI generation thread: {e}")
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self, ai_client):
        super().__init__()
        self.setWindowTitle("Mesly - Fullscreen OCR")
        self.resize(500, 600)

        # Tools
        self.stream_thread = None
        self.ai_client = ai_client
        self.ai_generation_thread = None
        self.audio_player = QMediaPlayer()
        self.audio_player.error.connect(self._on_audio_error)
        self.audio_player.stateChanged.connect(self._on_audio_state_changed)
        self.live_ai_enabled = False  # Disable live AI commentary by default. It's a token waste '-'
        self._raw_ai_response = ""  # Store raw markdown response
        # UI Setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("Mesly: Live AI Language Tutor")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)

        # Start/Stop Button
        self.btn_toggle_share = QPushButton("Start Screenshare")
        self.btn_toggle_share.setCheckable(True)
        self.btn_toggle_share.clicked.connect(self.toggle_sharing)
        self.btn_toggle_share.setStyleSheet("padding: 10px; font-size: 14px;")
        layout.addWidget(self.btn_toggle_share)

        # Toggle Live AI Commentary Button
        self.btn_toggle_ai = QPushButton("Enable Live AI Commentary (OFF)")
        self.btn_toggle_ai.setCheckable(True)
        self.btn_toggle_ai.setChecked(False)
        self.btn_toggle_ai.clicked.connect(self.toggle_live_ai)
        self.btn_toggle_ai.setStyleSheet("padding: 8px; font-size: 12px; background-color: #555;")
        layout.addWidget(self.btn_toggle_ai)

        # Preview Area
        self.lbl_preview = QLabel("Screen Preview")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setStyleSheet("border: 2px dashed #555; background: #222; color: #888;")
        self.lbl_preview.setMinimumSize(400, 300)
        self.lbl_preview.setScaledContents(True)
        layout.addWidget(self.lbl_preview)

        # Status Label
        self.lbl_status = QLabel("Ready to learn? Mesly will watch your screen and tutor you while you try learning a language.")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setWordWrap(True)
        layout.addWidget(self.lbl_status)

        # AI Response Area
        ai_label = QLabel("AI Language Tutor Response:")
        ai_label.setStyleSheet("font-weight: bold; padding-top: 10px;")
        layout.addWidget(ai_label)

        self.txt_ai_response = QTextEdit()
        self.txt_ai_response.setReadOnly(True)
        self.txt_ai_response.setPlaceholderText("AI explanations will appear here...")
        self.txt_ai_response.setStyleSheet("background: #1e1e1e; color: #d4d4d4; padding: 10px; font-family: monospace;")
        self.txt_ai_response.setMinimumHeight(150)
        layout.addWidget(self.txt_ai_response)

    def toggle_sharing(self, checked):
        if checked:
            self.stream_thread = ScreenShareThread(interval=5.0)  # 5 second delay between captures
            self.stream_thread.content_update.connect(self.handle_frame)
            self.stream_thread.start()

            self.btn_toggle_share.setText("Stop Fullscreen Capture")
            self.lbl_status.setText("Capturing fullscreen...")
            Logger.info("Started fullscreen capture (5 second interval)")
        else:
            if self.stream_thread:
                self.stream_thread.stop()
                self.stream_thread = None

            self.btn_toggle_share.setText("Start Fullscreen Capture")
            self.lbl_status.setText("Stopped")
            Logger.info("Stopped fullscreen capture")

    def toggle_live_ai(self, checked):
        """Toggle live AI commentary on/off"""
        self.live_ai_enabled = checked
        if checked:
            self.btn_toggle_ai.setText("Disable Live AI Commentary (ON)")
            self.btn_toggle_ai.setStyleSheet("padding: 8px; font-size: 12px; background-color: #2a7fff;")
            Logger.info("Live AI commentary enabled")
        else:
            self.btn_toggle_ai.setText("Enable Live AI Commentary (OFF)")
            self.btn_toggle_ai.setStyleSheet("padding: 8px; font-size: 12px; background-color: #555;")
            Logger.info("Live AI commentary disabled")

    def pil2pixmap(self, image):
        """Converts a PIL Image into a QPixmap for Qt display"""
        if image.mode == "RGB":
            r, g, b = image.split()
            image = Image.merge("RGB", (b, g, r))

        im2 = image.convert("RGBA")
        data = im2.tobytes("raw", "BGRA")
        qim = QImage(data, image.size[0], image.size[1], QImage.Format_ARGB32)
        pixmap = QPixmap.fromImage(qim)
        return pixmap

    def handle_frame(self, pil_image, extracted_text):
        """
        Receives the captured image and OCR text.
        Updates UI preview and can send to AI.
        """
        pixmap = self.pil2pixmap(pil_image)
        self.lbl_preview.setPixmap(pixmap)

        # Update Status Text
        if extracted_text:
            short_text = extracted_text.replace('\n', ' ')[:60]
            self.lbl_status.setText(f"OCR: {short_text}...")
            Logger.info(f"Extracted text ({len(extracted_text)} chars): {short_text}...")

            # Only send to AI if live commentary is enabled
            if self.live_ai_enabled:
                self._process_with_ai(extracted_text)
            else:
                Logger.debug("Live AI commentary disabled, skipping AI processing")

        else:
            self.lbl_status.setText("No text detected in current frame")

    def _process_with_ai(self, text: str):
        """
        Process extracted text with AI language tutor

        Args:
            text: OCR extracted text to analyze
        """
        if not text.strip():
            return

        # Don't start a new request if one is already running
        if self.ai_generation_thread and self.ai_generation_thread.isRunning():
            Logger.warning("AI generation already in progress, skipping new request")
            return

        # Get the system prompt for language tutor context
        system_prompt = LanguageTutorPrompts.get_system_prompt()

        # Use OCR context prompt since text came from screenshot
        user_prompt = get_tutor_prompt(text, mode="ocr")

        # Update UI with detailed status
        Logger.info("Sending text to AI language tutor...")
        provider_name = getattr(self.ai_client, 'provider', 'AI')
        self.lbl_status.setText(f"AI: Sending {len(text)} chars to {provider_name}...")
        self.txt_ai_response.setPlainText("Waiting for AI response...")

        # Create and start the AI generation thread
        self.lbl_status.setText(f"AI: {provider_name} is thinking...")
        self.txt_ai_response.clear()  # Clear previous response for streaming
        self._raw_ai_response = ""  # Reset raw response accumulator
        self.ai_generation_thread = AIGenerationThread(
            ai_client=self.ai_client,
            prompt=user_prompt,
            system_prompt=system_prompt
        )
        self.ai_generation_thread.streaming.connect(self._on_ai_streaming)
        self.ai_generation_thread.finished.connect(self._on_ai_response)
        self.ai_generation_thread.error.connect(self._on_ai_error)
        self.ai_generation_thread.start()

    def _process_custom_prompt(self, prompt: str, system_prompt: str = None):
        """
        Process a custom prompt with AI (used by screenshot handler)

        Args:
            prompt: Custom user prompt
            system_prompt: Optional system prompt (defaults to language tutor prompt)
        """
        if not prompt.strip():
            return

        # Don't start a new request if one is already running
        if self.ai_generation_thread and self.ai_generation_thread.isRunning():
            Logger.warning("AI generation already in progress, skipping new request")
            return

        # Use default system prompt if none provided
        if not system_prompt:
            system_prompt = LanguageTutorPrompts.get_system_prompt()

        # Update UI
        provider_name = getattr(self.ai_client, 'provider', 'AI')
        self.lbl_status.setText(f"AI: Processing screenshot request...")
        self.txt_ai_response.setPlainText("Waiting for AI response...")

        # Create and start the AI generation thread
        self.lbl_status.setText(f"AI: {provider_name} is thinking...")
        self.txt_ai_response.clear()
        self._raw_ai_response = ""
        self.ai_generation_thread = AIGenerationThread(
            ai_client=self.ai_client,
            prompt=prompt,
            system_prompt=system_prompt
        )
        self.ai_generation_thread.streaming.connect(self._on_ai_streaming)
        self.ai_generation_thread.finished.connect(self._on_ai_response)
        self.ai_generation_thread.error.connect(self._on_ai_error)
        self.ai_generation_thread.start()

    def _on_ai_streaming(self, chunk: str):
        """Handle streaming chunk from AI (updates UI in real-time)"""
        # Accumulate raw markdown response
        self._raw_ai_response += chunk

        # Strip markdown and display clean text
        clean_text = strip_markdown(self._raw_ai_response)
        self.txt_ai_response.setPlainText(clean_text)

        # Auto-scroll to bottom to show new text
        scrollbar = self.txt_ai_response.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        # Update status with current length (of clean text)
        current_len = len(clean_text)
        provider_name = getattr(self.ai_client, 'provider', 'AI')
        self.lbl_status.setText(f"AI: {provider_name} generating... ({current_len} chars)")

    def _on_ai_response(self, ai_response: str):
        """Handle AI response completion from background thread"""
        # Strip markdown from final response
        clean_response = strip_markdown(ai_response)

        Logger.info(f"AI response received ({len(ai_response)} chars, {len(clean_response)} clean)")
        self.lbl_status.setText(f"AI: Response complete ({len(clean_response)} chars). Generating audio...")

        # Ensure the UI shows the clean version
        self.txt_ai_response.setPlainText(clean_response)

        # Debug TTS selection
        Logger.info(f"TTS Check: HAS_CLOUD_TTS={HAS_CLOUD_TTS}, GOOGLE_CLOUD_PROJECT={os.getenv('GOOGLE_CLOUD_PROJECT')}, GOOGLE_APPLICATION_CREDENTIALS={os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")

        try:
            # Try Gemini Cloud TTS first if available and configured
            if HAS_CLOUD_TTS and self._use_gemini_tts():
                self._generate_gemini_audio(clean_response)
            else:
                # Fallback to gTTS
                self._generate_gtts_audio(clean_response)
        except Exception as e:
            Logger.error(f"Failed to generate or play audio: {e}")
            self.lbl_status.setText(f"AI: Response complete (audio failed)")

    def _use_gemini_tts(self) -> bool:
        """Check if we should use Gemini Cloud TTS (if Gemini is the provider and has API key)"""
        if not HAS_CLOUD_TTS:
            Logger.debug("google-cloud-texttospeech not installed, using gTTS")
            return False

        # Check if we have a Gemini API key in index (we'll use it for Cloud TTS)
        try:
            config = ConfigTemplate.get_config()
            for client in config.ai.clients:
                if client.provider.lower() == 'gemini' and client.api_key:
                    Logger.debug("Gemini API key found in index, will use Cloud TTS")
                    return True
        except Exception as e:
            Logger.debug(f"Error checking index: {e}")

        Logger.debug("No Gemini API key found, using gTTS")
        return False

    def _generate_gemini_audio(self, text: str):
        """Generate natural audio using Google Cloud Text-to-Speech with gemini-2.5-flash-tts"""
        try:
            Logger.info("Using Google Cloud TTS with gemini-2.5-flash-tts for natural voice...")

            # Get API key from index
            config = ConfigTemplate.get_config()
            api_key = None
            for client in config.ai.clients:
                if client.provider.lower() == 'gemini' and client.api_key:
                    api_key = client.api_key
                    break

            if not api_key:
                raise ValueError("Gemini API key not found")

            # Set API key as environment variable for authentication
            os.environ['GOOGLE_API_KEY'] = api_key

            # Initialize Cloud TTS client
            client = texttospeech.TextToSpeechClient()

            # Create synthesis input with the text
            synthesis_input = texttospeech.SynthesisInput(text=text)

            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                model_name="gemini-2.5-flash-tts",
                voice_config=texttospeech.VoiceConfig(
                    prebuilt_voice_config=texttospeech.PrebuiltVoiceConfig(
                        voice_name="Sulafat"
                    )
                )
            )

            # Configure audio output
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                sample_rate_hertz=24000,
            )

            # Generate speech
            Logger.debug("Sending TTS request to Google Cloud...")
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            # Save audio to file
            audio_file = "ai_response_gemini_tts.wav"
            Logger.info(f"Saving {len(response.audio_content)} bytes to {audio_file}")
            with open(audio_file, 'wb') as out:
                out.write(response.audio_content)

            # Play the audio
            audio_path = os.path.abspath(audio_file)
            Logger.info(f"Playing audio from: {audio_path}")

            # Stop any currently playing audio
            self.audio_player.stop()

            # Set and play the new audio
            self.audio_player.setMedia(QMediaContent(QUrl.fromLocalFile(audio_path)))
            self.audio_player.play()

            self.lbl_status.setText(f"AI: Playing natural Gemini TTS voice...")
            Logger.info(f"Gemini Cloud TTS audio playback started")

        except Exception as e:
            Logger.warning(f"Gemini Cloud TTS failed, falling back to gTTS: {e}")
            self._generate_gtts_audio(text)

    def _generate_gtts_audio(self, text: str):
        """Generate audio using gTTS (fallback)"""
        try:
            Logger.info("Using gTTS for audio...")
            tts = gTTS(text)
            audio_file = "ai_response.mp3"
            tts.save(audio_file)

            Logger.info(f"gTTS audio saved to {audio_file}")

            # Play the TTS audio
            audio_path = os.path.abspath(audio_file)
            Logger.info(f"Playing gTTS audio from: {audio_path}")

            # Stop any currently playing audio
            self.audio_player.stop()

            # Set and play the new audio
            self.audio_player.setMedia(QMediaContent(QUrl.fromLocalFile(audio_path)))
            self.audio_player.play()

            self.lbl_status.setText(f"AI: Playing audio response...")
            Logger.info(f"gTTS audio playback started")
        except Exception as e:
            Logger.error(f"gTTS audio generation/playback failed: {e}")
            self.lbl_status.setText(f"AI: Audio generation failed - {e}")

    def _on_ai_error(self, error_msg: str):
        """Handle AI error from background thread"""
        Logger.error(f"AI generation failed: {error_msg}")
        self.lbl_status.setText(f"AI: Error - {error_msg}")
        self.txt_ai_response.setPlainText(f"Error: {error_msg}")

    def _on_audio_error(self, error):
        """Handle audio playback errors"""
        error_string = self.audio_player.errorString()
        Logger.error(f"Audio playback error: {error} - {error_string}")
        self.lbl_status.setText(f"Audio error: {error_string}")

    def _on_audio_state_changed(self, state):
        """Log audio player state changes for debugging"""
        state_names = {
            0: "StoppedState",
            1: "PlayingState",
            2: "PausedState"
        }
        state_name = state_names.get(state, f"Unknown({state})")
        Logger.debug(f"Audio player state changed to: {state_name}")

