# widgets/custom_timer.py

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import QTimer, Qt


class CustomTimer(QWidget):
    """Таймер для фокус-сессии в виде круга"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.seconds = 0
        self.running = False

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel("00:00:00")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                font-size: 56px;
                font-weight: bold;
                color: #2C3E50;
                background-color: #F5F5F5;
                border-radius: 150px;
                padding: 40px;
                min-width: 250px;
                min-height: 250px;
            }
        """)
        self.layout.addWidget(self.label)

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)

    def start(self, start_seconds: int = 0):
        self.seconds = start_seconds
        self.running = True
        self.timer.start(1000)
        self._update_label()

    def set_seconds(self, seconds: int):
        self.seconds = seconds
        self._update_label()

    def pause(self):
        if self.running:
            self.running = False
            self.timer.stop()

    def resume(self):
        if not self.running:
            self.running = True
            self.timer.start(1000)

    def reset(self):
        self.seconds = 0
        self.running = False
        self.timer.stop()
        self._update_label()

    def _tick(self):
        if self.running:
            self.seconds += 1
            self._update_label()

    def _update_label(self):
        h = self.seconds // 3600
        m = (self.seconds % 3600) // 60
        s = self.seconds % 60
        self.label.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def get_seconds(self) -> int:
        return self.seconds