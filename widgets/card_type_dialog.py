# widgets/card_type_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QLineEdit, QWidget, QMessageBox
)
from PySide6.QtCore import Qt


class CardTypeDialog(QDialog):
    """Диалог выбора типа карточки и редактирования содержимого (немодальный)"""

    def __init__(self, selected_text: str, parent=None):
        super().__init__(parent)
        self.selected_text = selected_text
        self.card_type = "free"
        self.waiting_for_empty_answer = False  # флаг ожидания решения по пустому ответу

        self.setWindowTitle("Создание карточки")
        self.setModal(False)  # НЕ модальный!
        self.setMinimumWidth(500)

        self.setup_ui()
        self._select_type("free")

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Выберите тип карточки:"))

        type_row = QHBoxLayout()
        self.btn_free = QPushButton("📝 Свободная карточка")
        self.btn_qa = QPushButton("❓ Вопрос-Ответ")
        type_row.addWidget(self.btn_free)
        type_row.addWidget(self.btn_qa)
        layout.addLayout(type_row)

        layout.addSpacing(20)

        # Свободная карточка
        self.free_widget = QWidget()
        free_layout = QVBoxLayout(self.free_widget)
        free_layout.addWidget(QLabel("Содержание:"))
        self.free_text = QTextEdit()
        self.free_text.setPlainText(self.selected_text)
        self.free_text.setMinimumHeight(150)
        free_layout.addWidget(self.free_text)

        # Вопрос-Ответ
        self.qa_widget = QWidget()
        qa_layout = QVBoxLayout(self.qa_widget)
        qa_layout.addWidget(QLabel("Вопрос:"))
        self.question_input = QLineEdit()
        self.question_input.setText(self.selected_text)
        qa_layout.addWidget(self.question_input)

        qa_layout.addWidget(QLabel("Ответ:"))
        self.answer_input = QTextEdit()
        self.answer_input.setMinimumHeight(100)
        qa_layout.addWidget(self.answer_input)

        layout.addWidget(self.free_widget)
        layout.addWidget(self.qa_widget)

        layout.addSpacing(20)

        # Кнопки
        btn_row = QHBoxLayout()
        self.btn_cancel = QPushButton("Отмена")
        self.btn_create = QPushButton("Создать")
        btn_row.addStretch()
        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_create)
        layout.addLayout(btn_row)

        # Сигналы
        self.btn_free.clicked.connect(lambda: self._select_type("free"))
        self.btn_qa.clicked.connect(lambda: self._select_type("qa"))
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_create.clicked.connect(self._on_create_clicked)

    def _select_type(self, card_type: str):
        self.card_type = card_type

        if card_type == "free":
            self.free_widget.show()
            self.qa_widget.hide()
            self.btn_free.setStyleSheet("background-color: #4CAF50; color: white;")
            self.btn_qa.setStyleSheet("")
        else:
            self.free_widget.hide()
            self.qa_widget.show()
            self.btn_free.setStyleSheet("")
            self.btn_qa.setStyleSheet("background-color: #4CAF50; color: white;")

    def _on_create_clicked(self):
        """Обработчик нажатия на кнопку 'Создать'"""
        if self.card_type == "free":
            content = self.get_free_content()
            if content:
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Содержание карточки не может быть пустым")
        else:  # qa
            question = self.get_question()
            answer = self.get_answer()

            if question and answer:
                self.accept()
            elif question and not answer:
                # Нет ответа — спрашиваем
                reply = QMessageBox.question(
                    self,
                    "Нет ответа",
                    "Вы не заполнили ответ.\n\n"
                    "• Нажмите «Продолжить редактирование» — чтобы заполнить ответ\n"
                    "• Нажмите «Сохранить как простую карточку» — чтобы сохранить вопрос как свободную карточку",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                if reply == QMessageBox.Yes:
                    # Продолжить редактирование — ничего не делаем, окно остаётся открытым
                    self.waiting_for_empty_answer = False
                    return
                else:
                    # Сохранить как простую карточку
                    self.card_type = "free"
                    self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Заполните хотя бы вопрос")

    def get_free_content(self) -> str:
        return self.free_text.toPlainText().strip()

    def get_question(self) -> str:
        return self.question_input.text().strip()

    def get_answer(self) -> str:
        return self.answer_input.toPlainText().strip()