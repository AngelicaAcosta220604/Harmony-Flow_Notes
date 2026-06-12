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

# controllers/note_controller.py
from database.db_manager import db
from models.note import Note
from typing import List, Optional
from controllers.topic_controller import TopicController

class NoteController:
    """Контроллер для работы с заметками."""

    def _update_topic_timestamp(self, topic_id: int):
        """Обновляет время последнего изменения темы"""
        TopicController().update_timestamp(topic_id)

    def get_notes_by_topic(self, topic_id: int) -> List[Note]:
        """Возвращает все заметки темы."""
        rows = db.fetchall("SELECT * FROM notes WHERE topic_id = ? ORDER BY updated_at DESC", (topic_id,))
        return [Note.from_row(row) for row in rows]

    def get_note(self, note_id: int) -> Optional[Note]:
        """Возвращает заметку по id."""
        row = db.fetchone("SELECT * FROM notes WHERE id = ?", (note_id,))
        return Note.from_row(row) if row else None

    def create_note(self, topic_id: int, title: str = "", content: str = "") -> int:
        note_id = db.execute(
            "INSERT INTO notes (topic_id, title, content) VALUES (?, ?, ?)",
            (topic_id, title, content)
        )
        self._update_topic_timestamp(topic_id)  # <-- ДОБАВИТЬ
        return note_id

    def update_note(self, note_id: int, title: str = None, content: str = None) -> None:
        # Сначала получаем topic_id заметки
        note = self.get_note(note_id)
        if not note:
            return

        if title is not None:
            db.execute("UPDATE notes SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (title, note_id))
        if content is not None:
            db.execute("UPDATE notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (content, note_id))

        self._update_topic_timestamp(note.topic_id)  # <-- ДОБАВИТЬ

    def delete_note(self, note_id: int) -> None:
        # Сначала получаем topic_id заметки
        note = self.get_note(note_id)
        topic_id = note.topic_id if note else None

        db.execute("DELETE FROM notes WHERE id = ?", (note_id,))

        if topic_id:
            self._update_topic_timestamp(topic_id)

    def delete_note(self, note_id: int) -> None:
        """Удаляет заметку."""
        db.execute("DELETE FROM notes WHERE id = ?", (note_id,))

    def get_or_create_default_note(self, topic_id: int) -> Note:
        """Возвращает первую заметку темы или создаёт новую с заглушкой."""
        notes = self.get_notes_by_topic(topic_id)
        if notes:
            return notes[0]
        else:
            note_id = self.create_note(topic_id, title="Новая заметка", content="")
            return self.get_note(note_id)