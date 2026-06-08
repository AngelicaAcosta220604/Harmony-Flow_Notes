# Окно вопроса о концентрации (при бездействии)
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton
)
from PySide6.QtCore import Qt


class QuestionDialog(QDialog):
    """
    Прототип диалога создания карточки «Вопрос–Ответ».
    Используется в редакторе заметок.
    """

    def __init__(self, parent=None, prefilled_question: str = ""):
        super().__init__(parent)

        self.setWindowTitle("Создать карточку")
        self.setModal(True)
        self.setMinimumWidth(400)

        # Основной layout
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # ---------------------------------------------------------
        # Поле вопроса
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Вопрос:"))
        self.question_input = QLineEdit()
        self.question_input.setText(prefilled_question)
        layout.addWidget(self.question_input)

        # ---------------------------------------------------------
        # Поле ответа
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Ответ:"))
        self.answer_input = QTextEdit()
        layout.addWidget(self.answer_input)

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
    # Методы получения данных
    # ---------------------------------------------------------

    def get_question(self) -> str:
        return self.question_input.text().strip()

    def get_answer(self) -> str:
        return self.answer_input.toPlainText().strip()
