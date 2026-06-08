from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt


class AlertScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ALERT")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)

        layout = QVBoxLayout()

        label = QLabel("🚨 INTRUDER DETECTED 🚨")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setStyleSheet("""
            background-color: red;
            color: white;
            font-size: 50px;
            font-weight: bold;
        """)

        layout.addWidget(label)
        self.setLayout(layout)