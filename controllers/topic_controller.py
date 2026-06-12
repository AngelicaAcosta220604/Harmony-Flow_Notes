# controllers/topic_controller.py
"""
TopicController — контроллер для работы с темами и папками.
Реализует:
- создание темы
- получение списка тем
- получение темы по id
- обновление названия
- удаление темы
- каскадное удаление всех связанных данных (заметки, задачи, карточки, сессии)

Это один из ключевых модулей приложения.
"""

from database.db_manager import db
from models.topic import Topic
from utils.local_time import now_local_iso
from typing import List, Optional


class TopicController:
    """Контроллер для управления темами и папками."""

    def get_all_topics(self) -> List[Topic]:
        """Возвращает все темы и папки."""
        rows = db.fetchall("SELECT * FROM topics ORDER BY parent_id, name")
        return [Topic.from_row(row) for row in rows]

    def get_topic(self, topic_id: int) -> Optional[Topic]:
        """Возвращает тему по id."""
        row = db.fetchone("SELECT * FROM topics WHERE id = ?", (topic_id,))
        return Topic.from_row(row) if row else None

    def add_topic(self, name: str, parent_id: int = None, type: str = "topic") -> int:
        """Добавляет новую тему или папку. Возвращает id созданной записи."""
        now = now_local_iso()
        return db.execute(
            "INSERT INTO topics (name, parent_id, type, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (name, parent_id, type, now, now)
        )

    def rename_topic(self, topic_id: int, new_name: str) -> None:
        """Переименовывает тему."""
        now = now_local_iso()
        db.execute(
            "UPDATE topics SET name = ?, updated_at = ? WHERE id = ?",
            (new_name, now, topic_id)
        )

    def move_topic(self, topic_id: int, new_parent_id: Optional[int]) -> None:
        """Перемещает тему в другую папку."""
        now = now_local_iso()
        db.execute(
            "UPDATE topics SET parent_id = ?, updated_at = ? WHERE id = ?",
            (new_parent_id, now, topic_id)
        )

    def delete_topic(self, topic_id: int) -> None:
        """Удаляет тему и всё связанное с ней (каскадно)."""
        # Удаляем связанные данные (заметки, карточки, задачи, сессии)
        db.execute("DELETE FROM notes WHERE topic_id = ?", (topic_id,))
        db.execute("DELETE FROM flashcards WHERE topic_id = ?", (topic_id,))
        db.execute("DELETE FROM tasks WHERE topic_id = ?", (topic_id,))
        db.execute("DELETE FROM quick_notes WHERE topic_id = ?", (topic_id,))
        db.execute("DELETE FROM sessions WHERE topic_id = ?", (topic_id,))
        # Удаляем саму тему
        db.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
        # Удаляем дочерние темы (если есть)
        db.execute("DELETE FROM topics WHERE parent_id = ?", (topic_id,))

    def get_topic_tree(self) -> List[Topic]:
        """Возвращает все темы, отсортированные для построения дерева."""
        return self.get_all_topics()

    def update_timestamp(self, topic_id: int):
        """Обновляет updated_at темы (когда меняется содержимое)"""
        now = now_local_iso()
        db.execute("UPDATE topics SET updated_at = ? WHERE id = ?", (now, topic_id))