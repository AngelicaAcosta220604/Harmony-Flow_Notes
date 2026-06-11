# controllers/task_controller.py
"""
TaskController — контроллер для работы с задачами.

Реализует:
- создание задачи
- получение задач (по теме и всех)
- обновление
- изменение статуса
- определение просроченных задач
- удаление
- создание задачи из текста (заглушка для UI)
"""

# controllers/task_controller.py

from database.db_manager import db
from models.task import Task
from datetime import datetime


class TaskController:

    def create_task(self, title: str, description: str = "", topic_id: int = None, deadline: str = None) -> int:
        """Создаёт задачу"""
        now = datetime.now().isoformat()
        return db.execute(
            "INSERT INTO tasks (title, description, topic_id, deadline, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (title, description, topic_id, deadline, 'active', now)
        )

    def get_tasks_by_topic(self, topic_id: int) -> list:
        rows = db.fetchall(
            "SELECT * FROM tasks WHERE topic_id = ? ORDER BY deadline ASC, created_at DESC",
            (topic_id,)
        )
        return [Task.from_row(row) for row in rows]

    def get_all_tasks(self) -> list:
        rows = db.fetchall("SELECT * FROM tasks ORDER BY deadline ASC, created_at DESC")
        return [Task.from_row(row) for row in rows]

    def update_task_status(self, task_id: int, status: str):
        db.execute(
            "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
            (status, datetime.now().isoformat() if status == 'completed' else None, task_id)
        )

    def delete_task(self, task_id: int):
        db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def get_tasks_for_date(self, topic_id: int, date_str: str) -> list:
            """Возвращает задачи на конкретную дату."""
            rows = db.fetchall(
                """
                SELECT * FROM tasks 
                WHERE topic_id = ? AND DATE(deadline) = ?
                ORDER BY deadline ASC
                """,
                (topic_id, date_str)
            )
            return [Task.from_row(row) for row in rows]

    def update_task(self, task_id: int, title: str = None, description: str = None, deadline: str = None):
            """Обновляет задачу."""
            if title is not None:
                db.execute("UPDATE tasks SET title = ? WHERE id = ?", (title, task_id))
            if description is not None:
                db.execute("UPDATE tasks SET description = ? WHERE id = ?", (description, task_id))
            if deadline is not None:
                db.execute("UPDATE tasks SET deadline = ? WHERE id = ?", (deadline, task_id))