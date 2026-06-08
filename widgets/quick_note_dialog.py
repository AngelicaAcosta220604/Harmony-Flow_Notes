# Окно быстрой записи
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton
)
from PySide6.QtCore import Qt


class QuickNoteDialog(QDialog):
    """
    Прототип окна быстрой записи для фокус-сессии.
    Маленькое модальное окно 300×150.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Быстрая запись")
        self.setModal(True)
        self.setFixedSize(300, 150)

        # Основной layout
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # ---------------------------------------------------------
        # Поле ввода текста
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Записать мысль:"))

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Введите текст...")
        layout.addWidget(self.text_input)

        # ---------------------------------------------------------
        # Кнопки
        # ---------------------------------------------------------
        btn_row = QHBoxLayout()

        self.btn_save = QPushButton("Сохранить")
        self.btn_cancel = QPushButton("Отмена")

        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_cancel)

        layout.addLayout(btn_row)

        # ---------------------------------------------------------
        # Сигналы
        # ---------------------------------------------------------
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_save.clicked.connect(self.accept)

    # ---------------------------------------------------------
    # Получение текста
    # ---------------------------------------------------------

    def get_text(self) -> str:
        return self.text_input.toPlainText().strip()
