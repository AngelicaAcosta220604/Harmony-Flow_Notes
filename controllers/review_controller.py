# controllers/review_controller.py

from database.db_manager import db
from models.review_session import ReviewSession
from models.review_answer import ReviewAnswer
from controllers.flashcard_controller import FlashcardController
from datetime import datetime
from typing import List


class ReviewController:
    """Контроллер для управления сессиями повторения"""

    def __init__(self):
        self.flashcard_controller = FlashcardController()
        self.current_session_id = None
        self.session_cards = []  # список card_id в порядке показа
        self.current_card_index = 0
        self.session_start_time = None

    def start_session(self, topic_ids: List[int], include_free: bool = True, include_qa: bool = True) -> List:
        """Начинает новую сессию повторения"""
        # Получаем карточки для повторения
        cards = self.flashcard_controller.get_cards_for_review(topic_ids, include_free, include_qa)

        if not cards:
            return []

        # Сохраняем ID карточек
        self.session_cards = [card.id for card in cards]
        self.current_card_index = 0
        self.session_start_time = datetime.now()

        # Создаём запись о сессии в БД
        session_id = db.execute("""
            INSERT INTO review_sessions (session_date, total_cards, completed_cards, duration_minutes)
            VALUES (datetime('now'), ?, 0, 0)
        """, (len(cards),))

        self.current_session_id = session_id
        return cards

    def get_current_card(self):
        """Возвращает текущую карточку"""
        if self.current_card_index >= len(self.session_cards):
            return None
        return self.flashcard_controller.get_card(self.session_cards[self.current_card_index])

    def answer_card(self, rating: int, response_time_seconds: int = 0):
        """Обрабатывает ответ пользователя"""
        if self.current_card_index >= len(self.session_cards):
            return False

        card_id = self.session_cards[self.current_card_index]

        # Сохраняем ответ
        db.execute("""
            INSERT INTO review_answers (session_id, card_id, rating, response_time_seconds)
            VALUES (?, ?, ?, ?)
        """, (self.current_session_id, card_id, rating, response_time_seconds))

        # Обновляем статус карточки
        self.flashcard_controller.update_card_review_status(card_id, rating)

        # Переходим к следующей карточке
        self.current_card_index += 1

        # Обновляем прогресс сессии
        db.execute("""
            UPDATE review_sessions 
            SET completed_cards = completed_cards + 1,
                duration_minutes = CAST((JULIANDAY('now') - JULIANDAY(session_date)) * 24 * 60 AS INTEGER)
            WHERE id = ?
        """, (self.current_session_id,))

        return True

    def finish_session(self):
        """Завершает сессию"""
        if self.current_session_id:
            db.execute("""
                UPDATE review_sessions 
                SET duration_minutes = CAST((JULIANDAY('now') - JULIANDAY(session_date)) * 24 * 60 AS INTEGER)
                WHERE id = ?
            """, (self.current_session_id,))
            return True
        return False

    def is_session_complete(self) -> bool:
        """Проверяет, завершена ли сессия"""
        return self.current_card_index >= len(self.session_cards)

    def get_progress(self) -> dict:
        """Возвращает прогресс текущей сессии"""
        total = len(self.session_cards)
        completed = self.current_card_index
        return {
            "total": total,
            "completed": completed,
            "remaining": total - completed,
            "percent": int(completed / total * 100) if total > 0 else 0
        }