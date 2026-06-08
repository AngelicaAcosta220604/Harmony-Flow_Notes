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

from database.db_manager import db
from models.task import Task
from datetime import datetime


class TaskController:

    # ---------------------------------------------------------
    # СОЗДАНИЕ ЗАДАЧИ
    # ---------------------------------------------------------
    def create_task(
        self,
        title: str,
        description: str = "",
        topic_id: int | None = None,
        deadline: datetime | None = None
    ) -> int:
        """
        Создаёт новую задачу.
        topic_id может быть None — тогда это «общая задача».
        """
        query = """
            INSERT INTO tasks (title, description, topic_id, deadline)
            VALUES (?, ?, ?, ?)
        """
        cursor = db.execute(query, (title, description, topic_id, deadline))
        return cursor.lastrowid

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ВСЕХ ЗАДАЧ
    # ---------------------------------------------------------
    def get_all_tasks(self) -> list[Task]:
        """
        Возвращает все задачи.
        """
        rows = db.fetchall("SELECT * FROM tasks ORDER BY created_at DESC")
        return [Task.from_row(row) for row in rows]

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ЗАДАЧ ПО ТЕМЕ
    # ---------------------------------------------------------
    def get_tasks_by_topic(self, topic_id: int) -> list[Task]:
        """
        Возвращает задачи, привязанные к теме.
        """
        rows = db.fetchall(
            "SELECT * FROM tasks WHERE topic_id = ? ORDER BY created_at DESC",
            (topic_id,)
        )
        return [Task.from_row(row) for row in rows]

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ЗАДАЧИ ПО ID
    # ---------------------------------------------------------
    def get_task(self, task_id: int) -> Task | None:
        """
        Возвращает задачу по id.
        """
        row = db.fetchone("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return Task.from_row(row) if row else None

    # ---------------------------------------------------------
    # ОБНОВЛЕНИЕ ЗАДАЧИ
    # ---------------------------------------------------------
    def update_task(
        self,
        task_id: int,
        title: str,
        description: str,
        deadline: datetime | None
    ):
        """
        Обновляет заголовок, описание и дедлайн.
        """
        query = """
            UPDATE tasks
            SET title = ?, description = ?, deadline = ?
            WHERE id = ?
        """
        db.execute(query, (title, description, deadline, task_id))

    # ---------------------------------------------------------
    # ИЗМЕНЕНИЕ СТАТУСА
    # ---------------------------------------------------------
    def set_status(self, task_id: int, status: str):
        """
        Устанавливает статус задачи:
        - active
        - done
        - overdue
        """
        query = "UPDATE tasks SET status = ? WHERE id = ?"
        db.execute(query, (status, task_id))

    # ---------------------------------------------------------
    # ОТМЕТИТЬ КАК ВЫПОЛНЕННУЮ
    # ---------------------------------------------------------
    def mark_done(self, task_id: int):
        self.set_status(task_id, "done")

    # ---------------------------------------------------------
    # ПРОВЕРКА ПРОСРОЧКИ
    # ---------------------------------------------------------
    def update_overdue_tasks(self):
        """
        Обновляет статус всех задач, у которых дедлайн прошёл.
        """
        now = datetime.now()

        rows = db.fetchall("SELECT * FROM tasks WHERE status = 'active'")
        for row in rows:
            task = Task.from_row(row)

            if task.deadline is None:
                continue

            try:
                deadline_dt = datetime.fromisoformat(task.deadline)
            except:
                continue

            if deadline_dt < now:
                self.set_status(task.id, "overdue")

    # ---------------------------------------------------------
    # УДАЛЕНИЕ ЗАДАЧИ
    # ---------------------------------------------------------
    def delete_task(self, task_id: int):
        """
        Удаляет задачу.
        """
        db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    # ---------------------------------------------------------
    # СОЗДАНИЕ ЗАДАЧИ ИЗ ТЕКСТА (заглушка)
    # ---------------------------------------------------------
    def create_task_from_text(self, topic_id: int | None, text: str) -> int:
        """
        Создание задачи из выделенного текста заметки или из сессии.
        """
        print(f"[DEBUG] Создание задачи из текста: {text}")
        return