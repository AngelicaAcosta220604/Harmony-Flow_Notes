from database.db_manager import db
from models.task import Task
from datetime import datetime
from controllers.topic_controller import TopicController
from utils.local_time import now_local_iso


class TaskController:

    def _update_topic_timestamp(self, topic_id: int):
        if topic_id:
            TopicController().update_timestamp(topic_id)

    def create_task(self, title: str, description: str = "", topic_id: int = None, deadline: str = None) -> int:
        now = now_local_iso()
        result = db.execute(
            "INSERT INTO tasks (title, description, topic_id, deadline, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (title, description, topic_id, deadline, 'active', now)
        )
        self._update_topic_timestamp(topic_id)  # <-- ДОБАВИТЬ (если topic_id есть)
        return result

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
        # Сначала получаем topic_id задачи
        task = self.get_task(task_id)
        topic_id = task.topic_id if task else None

        db.execute(
            "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
            (status, now_local_iso() if status == 'completed' else None, task_id)
        )

        self._update_topic_timestamp(topic_id)

    def delete_task(self, task_id: int):
        # Сначала получаем topic_id задачи
        task = self.get_task(task_id)
        topic_id = task.topic_id if task else None

        db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

        self._update_topic_timestamp(topic_id)

    def get_tasks_for_date(self, topic_id: int, date_str: str) -> list:
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
        # Сначала получаем topic_id задачи
        task = self.get_task(task_id)
        topic_id = task.topic_id if task else None

        if title is not None:
            db.execute("UPDATE tasks SET title = ? WHERE id = ?", (title, task_id))
        if description is not None:
            db.execute("UPDATE tasks SET description = ? WHERE id = ?", (description, task_id))
        if deadline is not None:
            db.execute("UPDATE tasks SET deadline = ? WHERE id = ?", (deadline, task_id))

        self._update_topic_timestamp(topic_id)

    def get_task(self, task_id: int):
        """Возвращает задачу по ID"""
        row = db.fetchone("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return Task.from_row(row) if row else None