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


class TopicController:

    # ---------------------------------------------------------
    # СОЗДАНИЕ ТЕМЫ
    # ---------------------------------------------------------
    def create_topic(self, name: str, parent_id: int | None = None) -> int:
        """
        Создаёт новую тему или папку.
        Возвращает id созданной записи.
        """
        query = """
            INSERT INTO topics (name, parent_id)
            VALUES (?, ?)
        """
        cursor = db.execute(query, (name, parent_id))
        return cursor.lastrowid

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ВСЕХ ТЕМ
    # ---------------------------------------------------------
    def get_all_topics(self) -> list[Topic]:
        """
        Возвращает список всех тем в виде объектов Topic.
        """
        rows = db.fetchall("SELECT * FROM topics ORDER BY id ASC")
        return [Topic.from_row(row) for row in rows]

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ТЕМЫ ПО ID
    # ---------------------------------------------------------
    def get_topic(self, topic_id: int) -> Topic | None:
        """
        Возвращает тему по её id.
        """
        row = db.fetchone("SELECT * FROM topics WHERE id = ?", (topic_id,))
        return Topic.from_row(row) if row else None

    # ---------------------------------------------------------
    # ОБНОВЛЕНИЕ НАЗВАНИЯ ТЕМЫ
    # ---------------------------------------------------------
    def rename_topic(self, topic_id: int, new_name: str):
        """
        Переименовывает тему.
        """
        query = "UPDATE topics SET name = ? WHERE id = ?"
        db.execute(query, (new_name, topic_id))

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ВСЕХ ПОДТЕМ
    # ---------------------------------------------------------
    def get_children(self, parent_id: int) -> list[Topic]:
        """
        Возвращает список дочерних тем.
        """
        rows = db.fetchall("SELECT * FROM topics WHERE parent_id = ?", (parent_id,))
        return [Topic.from_row(row) for row in rows]

    # ---------------------------------------------------------
    # ПЕРЕМЕЩЕНИЕ ТЕМЫ
    # ---------------------------------------------------------
    def move_topic(self, topic_id: int, new_parent_id: int | None):
        """
        Меняет родителя темы.
        """
        query = "UPDATE topics SET parent_id = ? WHERE id = ?"
        db.execute(query, (new_parent_id, topic_id))

    # ---------------------------------------------------------
    # УДАЛЕНИЕ ТЕМЫ (КАСКАДНОЕ)
    # ---------------------------------------------------------
    def delete_topic(self, topic_id: int):
        """
        Удаляет тему и ВСЕ связанные данные:
        - заметки
        - задачи
        - карточки
        - сессии
        - логи состояния
        - быстрые записи
        - подтемы (рекурсивно)
        """

        # 1. Удаляем дочерние темы рекурсивно
        children = self.get_children(topic_id)
        for child in children:
            self.delete_topic(child.id)

        # 2. Удаляем заметки
        db.execute("DELETE FROM notes WHERE topic_id = ?", (topic_id,))

        # 3. Удаляем задачи
        db.execute("DELETE FROM tasks WHERE topic_id = ?", (topic_id,))

        # 4. Удаляем карточки
        db.execute("DELETE FROM flashcards WHERE topic_id = ?", (topic_id,))

        # 5. Удаляем быстрые записи
        db.execute("DELETE FROM quick_notes WHERE topic_id = ?", (topic_id,))

        # 6. Удаляем сессии и их логи
        sessions = db.fetchall("SELECT id FROM sessions WHERE topic_id = ?", (topic_id,))
        for s in sessions:
            session_id = s["id"]
            db.execute("DELETE FROM session_state_logs WHERE session_id = ?", (session_id,))
            db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

        # 7. Удаляем саму тему
        db.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
