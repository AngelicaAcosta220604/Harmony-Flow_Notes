# controllers/note_controller.py
"""
NoteController — контроллер для управления заметками.

Реализует:
- создание, редактирование, удаление заметок
- получение заметок по теме
- поиск заметок
- работа с содержимым заметок
"""

from database.db_manager import db
from models.note import Note
from utils.local_time import now_local_iso
from typing import List, Optional


class NoteController:
    """Контроллер для работы с заметками"""

    def __init__(self):
        pass

    def create_note(self, topic_id: int, title: str, content: str = "") -> int:
        """Создает новую заметку и возвращает её ID"""
        now = now_local_iso()
        query = """
            INSERT INTO notes (topic_id, title, content, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """
        return db.execute_insert(query, (topic_id, title, content, now, now))

    def get_note(self, note_id: int) -> Optional[Note]:
        """Возвращает заметку по ID"""
        row = db.fetchone("SELECT * FROM notes WHERE id = ?", (note_id,))
        return Note.from_row(row) if row else None

    def get_notes_by_topic(self, topic_id: int) -> List[Note]:
        """Возвращает все заметки темы"""
        rows = db.fetchall(
            "SELECT * FROM notes WHERE topic_id = ? ORDER BY updated_at DESC",
            (topic_id,)
        )
        return [Note.from_row(row) for row in rows]

    def update_note(self, note_id: int, title: str = None, content: str = None) -> bool:
        """Обновляет заметку"""
        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if content is not None:
            updates.append("content = ?")
            params.append(content)

        if not updates:
            return False

        updates.append("updated_at = ?")
        params.append(now_local_iso())
        params.append(note_id)

        query = f"UPDATE notes SET {', '.join(updates)} WHERE id = ?"
        return db.execute_update(query, params) > 0

    def delete_note(self, note_id: int) -> bool:
        """Удаляет заметку"""
        return db.execute_update("DELETE FROM notes WHERE id = ?", (note_id,)) > 0

    def search_notes(self, search_text: str) -> List[Note]:
        """Поиск заметок по тексту"""
        query = """
            SELECT * FROM notes 
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY updated_at DESC
        """
        search_pattern = f"%{search_text}%"
        rows = db.fetchall(query, (search_pattern, search_pattern))
        return [Note.from_row(row) for row in rows]

    def get_all_notes(self) -> List[Note]:
        """Возвращает все заметки"""
        rows = db.fetchall("SELECT * FROM notes ORDER BY updated_at DESC")
        return [Note.from_row(row) for row in rows]