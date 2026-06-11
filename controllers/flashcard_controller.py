# controllers/flashcard_controller.py
"""
FlashcardController — контроллер для работы с карточками.

Реализует:
- создание карточек (free / qa)
- получение карточек по теме
- получение карточки по id
- обновление
- удаление
- случайный и последовательный режимы
- создание карточки из выделенного текста (для UI)

Карточки — важная часть системы повторения.
"""
# controllers/flashcard_controller.py
# controllers/flashcard_controller.py

from database.db_manager import db
from models.flashcard import Flashcard


class FlashcardController:

    def create_free_card(self, topic_id: int, content: str, source_note_id: int = None) -> int:
        """Создаёт свободную карточку"""
        return db.execute(
            "INSERT INTO flashcards (topic_id, source_note_id, type, content) VALUES (?, ?, ?, ?)",
            (topic_id, source_note_id, "free", content)
        )

    def create_qa_card(self, topic_id: int, question: str, answer: str, source_note_id: int = None) -> int:
        """Создаёт карточку вопрос-ответ"""
        return db.execute(
            "INSERT INTO flashcards (topic_id, source_note_id, type, question, answer) VALUES (?, ?, ?, ?, ?)",
            (topic_id, source_note_id, "qa", question, answer)
        )

    def get_cards_by_topic(self, topic_id: int) -> list:
        rows = db.fetchall(
            "SELECT * FROM flashcards WHERE topic_id = ? ORDER BY created_at DESC",
            (topic_id,)
        )
        return [Flashcard.from_row(row) for row in rows]

    def get_cards_by_note(self, note_id: int) -> list:
        rows = db.fetchall(
            "SELECT * FROM flashcards WHERE source_note_id = ? ORDER BY created_at DESC",
            (note_id,)
        )
        return [Flashcard.from_row(row) for row in rows]

    def update_card(self, card_id: int, content: str = None, question: str = None, answer: str = None):
            """Обновляет карточку."""
            if content is not None:
                db.execute("UPDATE flashcards SET content = ? WHERE id = ?", (content, card_id))
            elif question is not None and answer is not None:
                db.execute("UPDATE flashcards SET question = ?, answer = ? WHERE id = ?", (question, answer, card_id))

    def delete_card(self, card_id: int):
            """Удаляет карточку."""
            db.execute("DELETE FROM flashcards WHERE id = ?", (card_id,))

    def get_all_cards(self) -> list:
        """Возвращает все карточки из всех тем (для глобального просмотра)"""
        rows = db.fetchall("SELECT * FROM flashcards ORDER BY created_at DESC")
        return [Flashcard.from_row(row) for row in rows]
