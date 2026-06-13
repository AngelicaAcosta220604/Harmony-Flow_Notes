# widgets/ping_dialog.py

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QTimer


class PingDialog(QDialog):
    """Диалог проверки активности пользователя"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Проверка активности")
        self.setModal(True)
        self.setFixedSize(350, 160)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.label = QLabel("Вы ещё здесь?\n\nСессия будет поставлена на паузу через 30 секунд")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.label)

        buttons = QHBoxLayout()
        buttons.setSpacing(15)

        self.continue_btn = QPushButton("✅ Да, я здесь")
        self.continue_btn.setDefault(True)
        self.continue_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.continue_btn.clicked.connect(self.accept)
        buttons.addWidget(self.continue_btn)

        self.pause_btn = QPushButton("⏸ Поставить на паузу")
        self.pause_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #F57C00; }
        """)
        self.pause_btn.clicked.connect(self.reject)
        buttons.addWidget(self.pause_btn)

        layout.addLayout(buttons)

        # Таймер авто-закрытия через 30 секунд
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.reject)
        self.timer.start(30000)