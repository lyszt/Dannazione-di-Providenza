from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PIL import Image

from ..capture.stream_thread import ScreenShareThread
from ..utils import Logger
from ..llm.local_llm_client import LocalLLMClient


class MainWindow(QMainWindow):
    def __init__(self, local_llm_client: LocalLLMClient):
        super().__init__()
        self.setWindowTitle("Mesly - Fullscreen OCR")
        self.resize(500, 600)

        # Tools
        self.stream_thread = None
        self.local_llm_client = local_llm_client

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

    def toggle_sharing(self, checked):
        if checked:
            self.stream_thread = ScreenShareThread()
            self.stream_thread.content_update.connect(self.handle_frame)
            self.stream_thread.start()

            self.btn_toggle_share.setText("Stop Fullscreen Capture")
            self.lbl_status.setText("Capturing fullscreen...")
            Logger.info("Started fullscreen capture")
        else:
            if self.stream_thread:
                self.stream_thread.stop()
                self.stream_thread = None

            self.btn_toggle_share.setText("Start Fullscreen Capture")
            self.lbl_status.setText("Stopped")
            Logger.info("Stopped fullscreen capture")

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
            Logger.info(f"Extracted Text: {extracted_text}")
            # TODO: Send to LLM
            # self.local_llm_client.send(extracted_text)
        else:
            self.lbl_status.setText("No text detected in current frame")

