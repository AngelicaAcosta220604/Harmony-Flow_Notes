# Диалог создания/редактирования задачи
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton,
    QComboBox, QDateEdit, QCheckBox
)
from PySide6.QtCore import Qt, QDate


class TaskDialog(QDialog):
    """
    Прототип диалога создания/редактирования задачи.
    Поля:
    - название
    - описание
    - тема (или "без темы")
    - дедлайн
    - напоминание
    """

    def __init__(self, parent=None, topics=None, default_topic=None):
        super().__init__(parent)

        self.setWindowTitle("Новая задача")
        self.setModal(True)
        self.setMinimumWidth(400)

        # Основной layout
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # ---------------------------------------------------------
        # Название
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Название задачи:"))
        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)

        # ---------------------------------------------------------
        # Описание
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Описание:"))
        self.desc_input = QTextEdit()
        layout.addWidget(self.desc_input)

        # ---------------------------------------------------------
        # Тема
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Тема:"))

        topic_row = QHBoxLayout()

        self.topic_select = QComboBox()
        self.no_topic_checkbox = QCheckBox("Без темы")

        # Заполняем список тем
        if topics:
            self.topic_select.addItems(topics)

        if default_topic:
            idx = self.topic_select.findText(default_topic)
            if idx >= 0:
                self.topic_select.setCurrentIndex(idx)

        topic_row.addWidget(self.topic_select)
        topic_row.addWidget(self.no_topic_checkbox)

        layout.addLayout(topic_row)

        # ---------------------------------------------------------
        # Дедлайн
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Дедлайн:"))

        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDate(QDate.currentDate())
        layout.addWidget(self.deadline_input)

        # ---------------------------------------------------------
        # Напоминание
        # ---------------------------------------------------------
        layout.addWidget(QLabel("Напоминание:"))

        self.reminder_select = QComboBox()
        self.reminder_select.addItems([
            "Нет",
            "За 10 минут",
            "За 30 минут",
            "За 1 час",
            "За 3 часа",
            "За 1 день"
        ])
        layout.addWidget(self.reminder_select)

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

    def get_title(self) -> str:
        return self.title_input.text().strip()

    def get_description(self) -> str:
        return self.desc_input.toPlainText().strip()

    def get_topic(self) -> str | None:
        if self.no_topic_checkbox.isChecked():
            return None
        return self.topic_select.currentText()

    def get_deadline(self) -> str:
        """Возвращает ISO-строку."""
        return self.deadline_input.date().toString("yyyy-MM-dd")

    def get_reminder(self) -> str:
        return self.reminder_select.currentText()
