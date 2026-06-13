# views/tasks_view.py

from PySide6.QtWidgets import QMessageBox
from widgets.silent_dialog import SilentMessageBox
from views.base_tasks_view import BaseTasksView
from widgets.task_dialog import TaskDialog


class TasksView(BaseTasksView):
    """Виджет для отображения и управления задачами конкретной темы (наследуется от BaseTasksView)"""

    def __init__(self, task_controller, topic_id: int, parent=None):
        self.topic_id = topic_id
        super().__init__(task_controller, parent)

    def get_tasks(self):
        """Возвращает задачи только для текущей темы"""
        return self.task_controller.get_tasks_by_topic(self.topic_id)

    def create_task(self):
        """Создаёт новую задачу для текущей темы"""
        dialog = TaskDialog(self)

        if dialog.exec():
            title = dialog.get_title()
            if title:
                self.task_controller.create_task(
                    title=title,
                    description=dialog.get_description(),
                    topic_id=self.topic_id,
                    deadline=dialog.get_deadline()
                )
                self.load_tasks()
                self.tasks_updated.emit()
                self.task_added.emit(None)
                SilentMessageBox.information(self, "Готово", f"Задача «{title}» создана!")