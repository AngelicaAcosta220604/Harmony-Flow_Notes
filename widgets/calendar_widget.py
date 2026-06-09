# widgets/calendar_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QCalendarWidget, QLabel, QListWidget, QListWidgetItem,
    QFrame  # ← правильно: QFrame, а не Frame
)
from PySide6.QtCore import Qt, Signal, QDate
from datetime import date


class CalendarWidget(QWidget):
    """Календарь для отображения задач по дням."""

    taskSelected = Signal(object)  # сигнал при выборе задачи

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # Переключение режимов
        mode_layout = QHBoxLayout()
        self.btn_day = QPushButton("День")
        self.btn_week = QPushButton("Неделя")
        self.btn_month = QPushButton("Месяц")
        mode_layout.addWidget(self.btn_day)
        mode_layout.addWidget(self.btn_week)
        mode_layout.addWidget(self.btn_month)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # Календарь
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self._on_date_selected)
        layout.addWidget(self.calendar)

        # Список задач на выбранный день (рамка)
        tasks_frame = QFrame()  # ← исправлено: QFrame
        tasks_frame.setFrameShape(QFrame.Box)
        tasks_layout = QVBoxLayout(tasks_frame)

        self.tasks_label = QLabel("Задачи на день:")
        tasks_layout.addWidget(self.tasks_label)

        self.tasks_list = QListWidget()
        self.tasks_list.itemClicked.connect(self._on_task_clicked)
        tasks_layout.addWidget(self.tasks_list)

        layout.addWidget(tasks_frame)

        # Подключение кнопок
        self.btn_day.clicked.connect(lambda: self._set_mode("day"))
        self.btn_week.clicked.connect(lambda: self._set_mode("week"))
        self.btn_month.clicked.connect(lambda: self._set_mode("month"))

        self._current_mode = "month"

    def _set_mode(self, mode: str):
        self._current_mode = mode
        # Здесь будет логика смены отображения
        print(f"[CalendarWidget] Режим: {mode}")

    def _on_date_selected(self, qdate: QDate):
        selected_date = date(qdate.year(), qdate.month(), qdate.day())
        print(f"[CalendarWidget] Выбрана дата: {selected_date}")
        # Здесь будет загрузка задач для даты

    def _on_task_clicked(self, item: QListWidgetItem):
        print(f"[CalendarWidget] Выбрана задача: {item.text()}")
        # Здесь будет сигнал для открытия задачи

    def update_tasks(self, tasks: list, selected_date: date):
        """Обновляет список задач для выбранной даты."""
        self.tasks_label.setText(f"Задачи на {selected_date}:")
        self.tasks_list.clear()
        for task in tasks:
            item = QListWidgetItem(task.get("title", str(task)))
            item.setData(Qt.UserRole, task)
            self.tasks_list.addItem(item)