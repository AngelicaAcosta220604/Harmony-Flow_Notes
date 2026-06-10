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
# controllers/topic_controller.py
from database.db_manager import db
from models.topic import Topic
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
        return db.execute(
            "INSERT INTO topics (name, parent_id, type) VALUES (?, ?, ?)",
            (name, parent_id, type)
        )

    def rename_topic(self, topic_id: int, new_name: str) -> None:
        db.execute(
            "UPDATE topics SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_name, topic_id)
        )

    def move_topic(self, topic_id: int, new_parent_id: Optional[int]) -> None:
        db.execute(
            "UPDATE topics SET parent_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_parent_id, topic_id)
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
