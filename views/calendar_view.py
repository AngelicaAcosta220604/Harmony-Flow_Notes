from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class CalendarView(QWidget):
    """
    Календарь + задачи по датам.
    """

    def __init__(self, calendar_controller, task_controller, parent=None):
        super().__init__(parent)
        self.calendar_controller = calendar_controller
        self.task_controller = task_controller

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Календарь"))

    def refresh(self):
        """Обновление календаря и задач."""
        pass
