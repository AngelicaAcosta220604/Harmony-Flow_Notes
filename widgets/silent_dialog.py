# widgets/silent_dialog.py

from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt


class SilentMessageBox(QDialog):
    """Модальное окно без звука"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setMinimumWidth(350)
        self.setMinimumHeight(150)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 28px;")
        layout.addWidget(self.icon_label)

        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.text_label)

        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        layout.addLayout(self.button_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #CCC;
                border-radius: 8px;
            }
            QPushButton {
                padding: 5px 12px;
                border: 1px solid #CCC;
                border-radius: 4px;
                background-color: #F0F0F0;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)

    @staticmethod
    def information(parent, title, text):
        dialog = SilentMessageBox(parent)
        dialog.setWindowTitle(title)
        dialog.icon_label.setText("ℹ️")
        dialog.text_label.setText(text)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(dialog.accept)
        dialog.button_layout.addWidget(ok_btn)
        dialog.button_layout.addStretch()

        return dialog.exec()

    @staticmethod
    def warning(parent, title, text):
        dialog = SilentMessageBox(parent)
        dialog.setWindowTitle(title)
        dialog.icon_label.setText("⚠️")
        dialog.text_label.setText(text)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(dialog.accept)
        dialog.button_layout.addWidget(ok_btn)
        dialog.button_layout.addStretch()

        return dialog.exec()

    @staticmethod
    def question(parent, title, text):
        dialog = SilentMessageBox(parent)
        dialog.setWindowTitle(title)
        dialog.icon_label.setText("❓")
        dialog.text_label.setText(text)

        yes_btn = QPushButton("Да")
        no_btn = QPushButton("Нет")

        yes_btn.clicked.connect(lambda: dialog.done(QMessageBox.Yes))
        no_btn.clicked.connect(lambda: dialog.done(QMessageBox.No))

        dialog.button_layout.addWidget(yes_btn)
        dialog.button_layout.addWidget(no_btn)
        dialog.button_layout.addStretch()

        return dialog.exec()