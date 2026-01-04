from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QComboBox, QLabel, QHBoxLayout)
from PyQt5.QtCore import Qt
from ..capture.window_selector import WindowSelector
from ..capture.stream_thread import ScreenShareThread
from ..utils import Logger


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mesly")
        self.resize(400, 300)

        # Tools
        self.window_selector = WindowSelector()
        self.stream_thread = None

        # UI Setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 1. Window Selection Row
        sel_layout = QHBoxLayout()
        self.combo_windows = QComboBox()
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.refresh_window_list)

        sel_layout.addWidget(QLabel("Target:"))
        sel_layout.addWidget(self.combo_windows, 1)  # Stretch factor 1
        sel_layout.addWidget(self.btn_refresh)
        layout.addLayout(sel_layout)

        # 2. Controls
        self.btn_toggle_share = QPushButton("Start Live Sharing")
        self.btn_toggle_share.setCheckable(True)
        self.btn_toggle_share.clicked.connect(self.toggle_sharing)
        layout.addWidget(self.btn_toggle_share)

        # 3. Preview/Status Label
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_status)

        # Initial Load
        self.refresh_window_list()

    def refresh_window_list(self):
        self.combo_windows.clear()
        self.combo_windows.addItem("Full Screen", None)  # Default option

        windows = self.window_selector.get_window_list()
        for title in windows:
            self.combo_windows.addItem(title, title)

        Logger.info(f"Found {len(windows)} windows")

    def toggle_sharing(self, checked):
        if checked:
            target = self.combo_windows.currentData()  # Returns title or None
            self.stream_thread = ScreenShareThread(target_window_title=target)
            self.stream_thread.frame_captured.connect(self.handle_frame)
            self.stream_thread.start()

            self.btn_toggle_share.setText("Stop Live Sharing")
            self.combo_windows.setEnabled(False)  # Lock selection while running
            self.lbl_status.setText(f"Sharing: {target if target else 'Full Screen'}")
        else:
            # STOP
            if self.stream_thread:
                self.stream_thread.stop()
                self.stream_thread = None

            self.btn_toggle_share.setText("Start Live Sharing")
            self.combo_windows.setEnabled(True)
            self.lbl_status.setText("Stopped")

    def handle_frame(self, pil_image):
        # Visual feedback that it's working
        timestamp = pil_image.size
        self.lbl_status.setText(f"Live: Frame captured {timestamp}")

        # TODO: Pass 'pil_image' to  AI/OCR function here
        # self.ai_processor.process(pil_image)