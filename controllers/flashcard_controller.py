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

from database.db_manager import db
from models.flashcard import Flashcard
import random


class FlashcardController:

    # ---------------------------------------------------------
    # СОЗДАНИЕ КАРТОЧКИ
    # ---------------------------------------------------------
    def create_flashcard(
        self,
        topic_id: int,
        type: str,
        question: str | None = None,
        answer: str | None = None
    ) -> int:
        """
        Создаёт карточку.
        type:
            - 'free' — свободная карточка (только текст)
            - 'qa'   — вопрос-ответ
        """
        query = """
            INSERT INTO flashcards (topic_id, type, question, answer)
            VALUES (?, ?, ?, ?)
        """
        cursor = db.execute(query, (topic_id, type, question, answer))
        return cursor.lastrowid

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ВСЕХ КАРТОЧЕК ПО ТЕМЕ
    # ---------------------------------------------------------
    def get_flashcards_by_topic(self, topic_id: int) -> list[Flashcard]:
        """
        Возвращает список карточек по теме.
        """
        rows = db.fetchall(
            "SELECT * FROM flashcards WHERE topic_id = ? ORDER BY id ASC",
            (topic_id,)
        )
        return [Flashcard.from_row(row) for row in rows]

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ КАРТОЧКИ ПО ID
    # ---------------------------------------------------------
    def get_flashcard(self, card_id: int) -> Flashcard | None:
        """
        Возвращает карточку по id.
        """
        row = db.fetchone("SELECT * FROM flashcards WHERE id = ?", (card_id,))
        return Flashcard.from_row(row) if row else None

    # ---------------------------------------------------------
    # ОБНОВЛЕНИЕ КАРТОЧКИ
    # ---------------------------------------------------------
    def update_flashcard(
        self,
        card_id: int,
        question: str | None,
        answer: str | None
    ):
        """
        Обновляет содержимое карточки.
        """
        query = """
            UPDATE flashcards
            SET question = ?, answer = ?
            WHERE id = ?
        """
        db.execute(query, (question, answer, card_id))

    # ---------------------------------------------------------
    # УДАЛЕНИЕ КАРТОЧКИ
    # ---------------------------------------------------------
    def delete_flashcard(self, card_id: int):
        """
        Удаляет карточку.
        """
        db.execute("DELETE FROM flashcards WHERE id = ?", (card_id,))

    # ---------------------------------------------------------
    # СЛУЧАЙНЫЙ РЕЖИМ
    # ---------------------------------------------------------
    def get_random_flashcard(self, topic_id: int) -> Flashcard | None:
        """
        Возвращает случайную карточку по теме.
        """
        cards = self.get_flashcards_by_topic(topic_id)
        return random.choice(cards) if cards else None

    # ---------------------------------------------------------
    # ПОСЛЕДОВАТЕЛЬНЫЙ РЕЖИМ
    # ---------------------------------------------------------
    def get_next_flashcard(self, topic_id: int, current_id: int | None) -> Flashcard | None:
        """
        Возвращает следующую карточку по порядку.
        Если current_id = None — возвращает первую.
        """
        cards = self.get_flashcards_by_topic(topic_id)
        if not cards:
            return None

        if current_id is None:
            return cards[0]

        for i, card in enumerate(cards):
            if card.id == current_id and i + 1 < len(cards):
                return cards[i + 1]

        return None  # если дошли до конца

    # ---------------------------------------------------------
    # СОЗДАНИЕ КАРТОЧКИ ИЗ ТЕКСТА (для заметок)
    # ---------------------------------------------------------
    def create_flashcard_from_text(self, topic_id: int, text: str) -> int:
        """
        Создаёт свободную карточку из выделенного текста заметки.
        """
        return self.create_flashcard(
            topic_id=topic_id,
            type="free",
            question=text,
            answer=None
        )
