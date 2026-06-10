# widgets/ping_dialog.py

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QTimer


class PingDialog(QDialog):
    """Диалог проверки активности пользователя"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Проверка активности")
        self.setModal(True)
        self.setFixedSize(300, 150)

        layout = QVBoxLayout(self)

        self.label = QLabel("Вы ещё здесь?\n\nСессия будет поставлена на паузу через 30 секунд")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        buttons = QHBoxLayout()
        self.continue_btn = QPushButton("Продолжить")
        self.continue_btn.setDefault(True)
        self.continue_btn.clicked.connect(self.accept)
        buttons.addWidget(self.continue_btn)

        layout.addLayout(buttons)

        # Таймер авто-закрытия через 30 секунд
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.reject)
        self.timer.start(30000)