# controllers/topic_controller.py
"""
TopicController — контроллер для работы с темами и папками.
"""

from database.db_manager import db
from models.topic import Topic
from utils.local_time import now_local_iso
from typing import List, Optional


class TopicController:
    """Контроллер для управления темами и папками."""

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Нормализует имя для сравнения (удаляет пробелы и приводит к нижнему регистру)."""
        return name.replace(" ", "").lower()

    def _is_name_unique(self, name: str, type: str, parent_id: int = None, exclude_id: int = None) -> bool:
        """
        Проверяет уникальность имени.

        Правила:
        - Папки уникальны в рамках одной родительской папки
        - Темы уникальны в рамках одной родительской папки
        - Папка не может иметь имя, совпадающее с именем родительской папки
        """
        normalized_new = self._normalize_name(name)

        # Проверка: папка не может иметь имя родительской папки
        if type == "folder" and parent_id is not None:
            parent = self.get_topic(parent_id)
            if parent and self._normalize_name(parent.name) == normalized_new:
                return False

        # Получаем все элементы с таким же parent_id и типом
        if parent_id is None:
            rows = db.fetchall(
                "SELECT id, name FROM topics WHERE type = ? AND parent_id IS NULL",
                (type,)
            )
        else:
            rows = db.fetchall(
                "SELECT id, name FROM topics WHERE type = ? AND parent_id = ?",
                (type, parent_id)
            )

        for row in rows:
            if exclude_id is not None and row["id"] == exclude_id:
                continue

            normalized_existing = self._normalize_name(row["name"])
            if normalized_new == normalized_existing:
                return False

        return True

    def get_all_topics(self) -> List[Topic]:
        """Возвращает все темы и папки."""
        rows = db.fetchall("SELECT * FROM topics ORDER BY parent_id, name")
        return [Topic.from_row(row) for row in rows]

    def get_topic(self, topic_id: int) -> Optional[Topic]:
        """Возвращает тему по id."""
        row = db.fetchone("SELECT * FROM topics WHERE id = ?", (topic_id,))
        return Topic.from_row(row) if row else None

    def add_topic(self, name: str, parent_id: int = None, type: str = "topic") -> int:
        """
        Добавляет новую тему или папку.
        Выбрасывает ValueError, если имя не уникально или совпадает с именем родительской папки.
        """
        # Специальная проверка для папки на совпадение с родительской
        if type == "folder" and parent_id is not None:
            parent = self.get_topic(parent_id)
            if parent and self._normalize_name(parent.name) == self._normalize_name(name):
                raise ValueError(f"Папка не может иметь имя, совпадающее с именем родительской папки «{parent.name}»")

        if not self._is_name_unique(name, type, parent_id):
            if type == "folder":
                if parent_id is None:
                    raise ValueError(f"Папка с названием «{name}» уже существует в корне")
                else:
                    parent = self.get_topic(parent_id)
                    parent_name = parent.name if parent else "этой папке"
                    raise ValueError(f"Папка с названием «{name}» уже существует в папке «{parent_name}»")
            else:
                if parent_id is None:
                    raise ValueError(f"Тема с названием «{name}» уже существует в корне")
                else:
                    parent = self.get_topic(parent_id)
                    parent_name = parent.name if parent else "этой папке"
                    raise ValueError(f"Тема с названием «{name}» уже существует в папке «{parent_name}»")

        now = now_local_iso()
        return db.execute(
            "INSERT INTO topics (name, parent_id, type, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (name, parent_id, type, now, now)
        )

    def rename_topic(self, topic_id: int, new_name: str) -> None:
        """
        Переименовывает тему или папку.
        Выбрасывает ValueError, если новое имя не уникально или совпадает с именем родительской папки.
        """
        current = self.get_topic(topic_id)
        if not current:
            raise ValueError("Элемент не найден")

        # Специальная проверка для папки на совпадение с родительской
        if current.type == "folder" and current.parent_id is not None:
            parent = self.get_topic(current.parent_id)
            if parent and self._normalize_name(parent.name) == self._normalize_name(new_name):
                raise ValueError(f"Папка не может иметь имя, совпадающее с именем родительской папки «{parent.name}»")

        if not self._is_name_unique(new_name, current.type, current.parent_id, exclude_id=topic_id):
            if current.type == "folder":
                if current.parent_id is None:
                    raise ValueError(f"Папка с названием «{new_name}» уже существует в корне")
                else:
                    parent = self.get_topic(current.parent_id)
                    parent_name = parent.name if parent else "этой папке"
                    raise ValueError(f"Папка с названием «{new_name}» уже существует в папке «{parent_name}»")
            else:
                if current.parent_id is None:
                    raise ValueError(f"Тема с названием «{new_name}» уже существует в корне")
                else:
                    parent = self.get_topic(current.parent_id)
                    parent_name = parent.name if parent else "этой папке"
                    raise ValueError(f"Тема с названием «{new_name}» уже существует в папке «{parent_name}»")

        now = now_local_iso()
        db.execute(
            "UPDATE topics SET name = ?, updated_at = ? WHERE id = ?",
            (new_name, now, topic_id)
        )

    def move_topic(self, topic_id: int, new_parent_id: Optional[int]) -> None:
        """
        Перемещает тему или папку в другую папку.
        Выбрасывает ValueError, если:
        - в целевой папке уже есть элемент с таким же именем
        - папка пытается стать родителем самой себя
        - папка пытается быть перемещена в свою дочернюю папку
        - папка пытается получить имя, совпадающее с именем родительской
        """
        current = self.get_topic(topic_id)
        if not current:
            raise ValueError("Элемент не найден")

        # Проверка: нельзя переместить папку в саму себя
        if current.type == "folder" and current.id == new_parent_id:
            raise ValueError("Нельзя переместить папку в саму себя")

        # Проверка: нельзя переместить папку в её дочернюю папку
        if current.type == "folder" and new_parent_id is not None:
            if self._is_child_of(new_parent_id, current.id):
                raise ValueError("Нельзя переместить папку в её собственную вложенную папку")

        # Специальная проверка для папки на совпадение с новой родительской папкой
        if current.type == "folder" and new_parent_id is not None:
            new_parent = self.get_topic(new_parent_id)
            if new_parent and self._normalize_name(new_parent.name) == self._normalize_name(current.name):
                raise ValueError(
                    f"Папка не может иметь имя, совпадающее с именем родительской папки «{new_parent.name}»")

        # Проверяем уникальность имени в целевой папке
        if not self._is_name_unique(current.name, current.type, new_parent_id, exclude_id=topic_id):
            if current.type == "folder":
                if new_parent_id is None:
                    raise ValueError(f"Папка с названием «{current.name}» уже существует в корне")
                else:
                    parent = self.get_topic(new_parent_id)
                    parent_name = parent.name if parent else "этой папке"
                    raise ValueError(f"Папка с названием «{current.name}» уже существует в папке «{parent_name}»")
            else:
                if new_parent_id is None:
                    raise ValueError(f"Тема с названием «{current.name}» уже существует в корне")
                else:
                    parent = self.get_topic(new_parent_id)
                    parent_name = parent.name if parent else "этой папке"
                    raise ValueError(f"Тема с названием «{current.name}» уже существует в папке «{parent_name}»")

        now = now_local_iso()
        db.execute(
            "UPDATE topics SET parent_id = ?, updated_at = ? WHERE id = ?",
            (new_parent_id, now, topic_id)
        )

    def _is_child_of(self, child_id: int, parent_id: int) -> bool:
        """Проверяет, является ли child_id потомком parent_id."""
        if child_id == parent_id:
            return True

        child = self.get_topic(child_id)
        if not child or child.parent_id is None:
            return False

        return self._is_child_of(child.parent_id, parent_id)

    def delete_topic(self, topic_id: int) -> None:
        """Удаляет тему и всё связанное с ней (каскадно)."""
        db.execute("DELETE FROM notes WHERE topic_id = ?", (topic_id,))
        db.execute("DELETE FROM flashcards WHERE topic_id = ?", (topic_id,))
        db.execute("DELETE FROM tasks WHERE topic_id = ?", (topic_id,))
        db.execute("DELETE FROM quick_notes WHERE topic_id = ?", (topic_id,))
        db.execute("DELETE FROM sessions WHERE topic_id = ?", (topic_id,))
        db.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
        db.execute("DELETE FROM topics WHERE parent_id = ?", (topic_id,))

    def get_topic_tree(self) -> List[Topic]:
        """Возвращает все темы, отсортированные для построения дерева."""
        return self.get_all_topics()

    def update_timestamp(self, topic_id: int):
        """Обновляет updated_at темы (когда меняется содержимое)"""
        now = now_local_iso()
        db.execute("UPDATE topics SET updated_at = ? WHERE id = ?", (now, topic_id))