from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QShortcut, QWidget, QMainWindow, QLabel
import sys

def handle_screenshot():
    print("Translation requested.")



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mesly: Live Language Tutor")
        self.resize(300, 200)

        label = QLabel("Press Ctrl+Shift+T", self)
        self.setCentralWidget(label)
