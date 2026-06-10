# widgets/task_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QDateEdit, QComboBox
)
from PySide6.QtCore import Qt, QDate


class TaskDialog(QDialog):
    """Диалог создания задачи с датой и выбором времени"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новая задача")
        self.setModal(True)
        self.setMinimumWidth(400)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Название
        layout.addWidget(QLabel("Название задачи:"))
        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)

        # Описание
        layout.addWidget(QLabel("Описание (необязательно):"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(100)
        layout.addWidget(self.desc_input)

        # Дедлайн
        layout.addWidget(QLabel("Дедлайн (необязательно):"))

        # Дата через календарь
        date_row = QHBoxLayout()
        self.deadline_date = QDateEdit()
        self.deadline_date.setCalendarPopup(True)
        self.deadline_date.setDate(QDate.currentDate())
        self.deadline_date.setMinimumWidth(150)

        self.no_deadline_check = QPushButton("Без дедлайна")
        self.no_deadline_check.setCheckable(True)
        self.no_deadline_check.setStyleSheet(
            "QPushButton { background-color: #F0F0F0; } QPushButton:checked { background-color: #4CAF50; color: white; }"
        )
        self.no_deadline_check.toggled.connect(self._toggle_deadline)

        date_row.addWidget(self.deadline_date)
        date_row.addWidget(self.no_deadline_check)
        layout.addLayout(date_row)

        layout.addSpacing(10)

        # Время (часы и минуты) — простые выпадающие списки
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Время:"))

        # Часы 0-23
        self.hour_combo = QComboBox()
        for h in range(24):
            self.hour_combo.addItem(f"{h:02d}", h)
        self.hour_combo.setCurrentIndex(12)  # 12:00 по умолчанию
        time_layout.addWidget(self.hour_combo)

        time_layout.addWidget(QLabel(":"))

        # Минуты 0-59
        self.minute_combo = QComboBox()
        for m in range(0, 60, 5):  # шаг 5 минут
            self.minute_combo.addItem(f"{m:02d}", m)
        self.minute_combo.setCurrentIndex(0)
        time_layout.addWidget(self.minute_combo)

        time_layout.addStretch()
        layout.addLayout(time_layout)

        layout.addSpacing(20)

        # Кнопки
        btn_row = QHBoxLayout()
        self.btn_save = QPushButton("Сохранить")
        self.btn_cancel = QPushButton("Отмена")
        btn_row.addStretch()
        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_save)
        layout.addLayout(btn_row)

        # Сигналы
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_save.clicked.connect(self.accept)

    def _toggle_deadline(self, checked: bool):
        """Включает/выключает дедлайн"""
        enabled = not checked
        self.deadline_date.setEnabled(enabled)
        self.hour_combo.setEnabled(enabled)
        self.minute_combo.setEnabled(enabled)

    def get_title(self) -> str:
        return self.title_input.text().strip()

    def get_description(self) -> str:
        return self.desc_input.toPlainText().strip()

    def get_deadline(self) -> str:
        """Возвращает строку даты и времени или None"""
        if self.no_deadline_check.isChecked():
            return None

        date = self.deadline_date.date()
        hour = self.hour_combo.currentData()
        minute = self.minute_combo.currentData()

        deadline_str = f"{date.year()}-{date.month():02d}-{date.day():02d} {hour:02d}:{minute:02d}:00"
        return deadline_str