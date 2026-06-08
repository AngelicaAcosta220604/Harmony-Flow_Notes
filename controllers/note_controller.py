# controllers/note_controller.py
"""
NoteController — контроллер для работы с заметками.
Реализует:
- создание заметки
- получение заметок по теме
- получение заметки по id
- обновление содержимого
- автосохранение
- удаление заметки
- импорт .txt
- создание карточек/задач из выделенного текста (заглушки для UI)

Это один из ключевых модулей приложения.
"""

from database.db_manager import db
from models.note import Note
from datetime import datetime
from pathlib import Path


class NoteController:

    # ---------------------------------------------------------
    # СОЗДАНИЕ ЗАМЕТКИ
    # ---------------------------------------------------------
    def create_note(self, topic_id: int, title: str, content: str = "") -> int:
        """
        Создаёт новую заметку.
        Возвращает id созданной записи.
        """
        query = """
            INSERT INTO notes (topic_id, title, content)
            VALUES (?, ?, ?)
        """
        cursor = db.execute(query, (topic_id, title, content))
        return cursor.lastrowid

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ВСЕХ ЗАМЕТОК ПО ТЕМЕ
    # ---------------------------------------------------------
    def get_notes_by_topic(self, topic_id: int) -> list[Note]:
        """
        Возвращает список заметок, принадлежащих теме.
        """
        rows = db.fetchall(
            "SELECT * FROM notes WHERE topic_id = ? ORDER BY created_at DESC",
            (topic_id,)
        )
        return [Note.from_row(row) for row in rows]

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ЗАМЕТКИ ПО ID
    # ---------------------------------------------------------
    def get_note(self, note_id: int) -> Note | None:
        """
        Возвращает заметку по её id.
        """
        row = db.fetchone("SELECT * FROM notes WHERE id = ?", (note_id,))
        return Note.from_row(row) if row else None

    # ---------------------------------------------------------
    # ОБНОВЛЕНИЕ ЗАМЕТКИ
    # ---------------------------------------------------------
    def update_note(self, note_id: int, new_title: str, new_content: str):
        """
        Обновляет заголовок и содержимое заметки.
        Обновляет поле updated_at.
        """
        query = """
            UPDATE notes
            SET title = ?, content = ?, updated_at = ?
            WHERE id = ?
        """
        db.execute(query, (new_title, new_content, datetime.now(), note_id))

    # ---------------------------------------------------------
    # АВТОСОХРАНЕНИЕ
    # ---------------------------------------------------------
    def autosave(self, note_id: int, new_content: str):
        """
        Автосохранение заметки.
        Обновляет только содержимое и updated_at.
        """
        query = """
            UPDATE notes
            SET content = ?, updated_at = ?
            WHERE id = ?
        """
        db.execute(query, (new_content, datetime.now(), note_id))

    # ---------------------------------------------------------
    # УДАЛЕНИЕ ЗАМЕТКИ
    # ---------------------------------------------------------
    def delete_note(self, note_id: int):
        """
        Удаляет заметку.
        """
        db.execute("DELETE FROM notes WHERE id = ?", (note_id,))

    # ---------------------------------------------------------
    # ИМПОРТ .TXT ФАЙЛА
    # ---------------------------------------------------------
    def import_txt(self, topic_id: int, file_path: str) -> int:
        """
        Импортирует .txt файл как новую заметку.
        Название = имя файла.
        Содержимое = текст файла.
        """
        path = Path(file_path)

        if not path.exists() or not path.is_file():
            raise FileNotFoundError("Файл не найден")

        content = path.read_text(encoding="utf-8")
        title = path.stem  # имя файла без расширения

        return self.create_note(topic_id, title, content)

    # ---------------------------------------------------------
    # СОЗДАНИЕ КАРТОЧКИ ИЗ ВЫДЕЛЕННОГО ТЕКСТА (заглушка)
    # ---------------------------------------------------------
    def create_flashcard_from_text(self, topic_id: int, text: str):
        """
        Заглушка для UI.
        Контроллер карточек будет реализовывать реальную логику.
        """
        print(f"[DEBUG] Создание карточки из текста: {text}")

    # ---------------------------------------------------------
    # СОЗДАНИЕ ЗАДАЧИ ИЗ ВЫДЕЛЕННОГО ТЕКСТА (заглушка)
    # ---------------------------------------------------------
    def create_task_from_text(self, topic_id: int, text: str):
        """
        Заглушка для UI.
        Контроллер задач будет реализовывать реальную логику.
        """
        print(f"[DEBUG] Создание задачи из текста: {text}")
