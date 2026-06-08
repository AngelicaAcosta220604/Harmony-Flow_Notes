from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class TasksView(QWidget):
    """
    Экран задач.
    """

    def __init__(self, task_controller, topic_controller, parent=None):
        super().__init__(parent)
        self.task_controller = task_controller
        self.topic_controller = topic_controller

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Задачи"))

    def refresh(self):
        """Обновление списка задач."""
        pass
