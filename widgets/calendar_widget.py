# Календарь задач
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QSizePolicy, Frame
)
from PySide6.QtCore import Qt, QDate


class CalendarWidget(QWidget):
    """
    Прототип календаря (месяц).
    Позже сюда можно подключить CalendarController.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_date = QDate.currentDate()

        # Основной layout
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # ---------------------------------------------------------
        # Верхняя панель: переключатели (День / Неделя / Месяц)
        # ---------------------------------------------------------
        mode_bar = QHBoxLayout()

        self.btn_day = QPushButton("День")
        self.btn_week = QPushButton("Неделя")
        self.btn_month = QPushButton("Месяц")

        self.btn_month.setEnabled(False)  # активный режим

        mode_bar.addWidget(self.btn_day)
        mode_bar.addWidget(self.btn_week)
        mode_bar.addWidget(self.btn_month)
        mode_bar.addStretch()

        self.layout.addLayout(mode_bar)

        # ---------------------------------------------------------
        # Заголовок месяца
        # ---------------------------------------------------------
        self.month_label = QLabel()
        self.month_label.setAlignment(Qt.AlignCenter)
        self.month_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.month_label)

        # ---------------------------------------------------------
        # Сетка календаря
        # ---------------------------------------------------------
        self.grid = QGridLayout()
        self.layout.addLayout(self.grid)

        # Заголовки дней недели
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, name in enumerate(weekdays):
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-weight: bold;")
            self.grid.addWidget(lbl, 0, i)

        # Сетка дней (6 строк × 7 столбцов)
        self.day_cells = []
        for row in range(1, 7):
            row_cells = []
            for col in range(7):
                cell = QLabel("")
                cell.setAlignment(Qt.AlignCenter)
                cell.setFrameStyle(QLabel.Panel | QLabel.Raised)
                cell.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                cell.setMinimumHeight(40)
                row_cells.append(cell)
                self.grid.addWidget(cell, row, col)
            self.day_cells.append(row_cells)

        # Отрисовываем текущий месяц
        self.update_calendar()

    # ---------------------------------------------------------
    # Обновление календаря
    # ---------------------------------------------------------
    def update_calendar(self):
        """Заполняет сетку днями текущего месяца."""
        year = self.current_date.year()
        month = self.current_date.month()

        self.month_label.setText(self.current_date.toString("MMMM yyyy"))

        first_day = QDate(year, month, 1)
        start_col = (first_day.dayOfWeek() + 6) % 7  # Пн=0, Вс=6

        days_in_month = first_day.daysInMonth()

        # Очищаем сетку
        for row in self.day_cells:
            for cell in row:
                cell.setText("")
                cell.setStyleSheet("")

        # Заполняем числа
        day = 1
        row = 0
        col = start_col

        while day <= days_in_month:
            cell = self.day_cells[row][col]
            cell.setText(str(day))

            # Подсветка сегодняшнего дня
            if (
                day == QDate.currentDate().day() and
                month == QDate.currentDate().month() and
                year == QDate.currentDate().year()
            ):
                cell.setStyleSheet("background-color: #d0eaff; border: 1px solid #3399ff;")

            day += 1
            col += 1
            if col > 6:
                col = 0
                row += 1

    # ---------------------------------------------------------
    # Методы переключения месяца (можно подключить к кнопкам)
    # ---------------------------------------------------------
    def next_month(self):
        self.current_date = self.current_date.addMonths(1)
        self.update_calendar()

    def prev_month(self):
        self.current_date = self.current_date.addMonths(-1)
        self.update_calendar()
