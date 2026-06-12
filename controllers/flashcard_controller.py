# controllers/flashcard_controller.py

from database.db_manager import db
from models.flashcard import Flashcard
from controllers.topic_controller import TopicController

class FlashcardController:

    def _update_topic_timestamp(self, topic_id: int):
        TopicController().update_timestamp(topic_id)

    def create_free_card(self, topic_id: int, content: str, source_note_id: int = None) -> int:
        result = db.execute(
            "INSERT INTO flashcards (topic_id, source_note_id, type, content) VALUES (?, ?, ?, ?)",
            (topic_id, source_note_id, "free", content)
        )
        self._update_topic_timestamp(topic_id)  # <-- ДОБАВИТЬ
        return result

    def create_qa_card(self, topic_id: int, question: str, answer: str, source_note_id: int = None) -> int:
        result = db.execute(
            "INSERT INTO flashcards (topic_id, source_note_id, type, question, answer) VALUES (?, ?, ?, ?, ?)",
            (topic_id, source_note_id, "qa", question, answer)
        )
        self._update_topic_timestamp(topic_id)  # <-- ДОБАВИТЬ
        return result

    def get_card(self, card_id: int):
        """Возвращает одну карточку по ID"""
        row = db.fetchone("SELECT * FROM flashcards WHERE id = ?", (card_id,))
        if row:
            return Flashcard.from_row(row)
        return None

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

    def get_all_cards(self) -> list:
        """Возвращает все карточки из всех тем (для глобального просмотра)"""
        rows = db.fetchall("SELECT * FROM flashcards ORDER BY created_at DESC")
        return [Flashcard.from_row(row) for row in rows]

    def update_card(self, card_id: int, content: str = None, question: str = None, answer: str = None):
        # Сначала получаем topic_id карточки
        card = self.get_card(card_id)
        if not card:
            return

        if content is not None:
            db.execute("UPDATE flashcards SET content = ?, updated_at = datetime('now') WHERE id = ?",
                       (content, card_id))
        elif question is not None and answer is not None:
            db.execute("UPDATE flashcards SET question = ?, answer = ?, updated_at = datetime('now') WHERE id = ?",
                       (question, answer, card_id))

        self._update_topic_timestamp(card.topic_id)

    def delete_card(self, card_id: int):
        # Сначала получаем topic_id карточки
        card = self.get_card(card_id)
        topic_id = card.topic_id if card else None

        db.execute("DELETE FROM flashcards WHERE id = ?", (card_id,))

        if topic_id:
            self._update_topic_timestamp(topic_id)

    def get_cards_for_review(self, topic_ids: list, include_free: bool = True, include_qa: bool = True) -> list:
        """Возвращает карточки из выбранных тем для повторения"""
        if not topic_ids:
            return []

        placeholders = ','.join('?' * len(topic_ids))
        type_filter = []
        if include_free and include_qa:
            type_filter = ["free", "qa"]
        elif include_free:
            type_filter = ["free"]
        elif include_qa:
            type_filter = ["qa"]
        else:
            return []

        type_placeholders = ','.join('?' * len(type_filter))

        query = f"""
            SELECT * FROM flashcards 
            WHERE topic_id IN ({placeholders})
            AND type IN ({type_placeholders})
            AND is_active = 1
            ORDER BY 
                CASE review_status 
                    WHEN 'new' THEN 0 
                    WHEN 'learning' THEN 1 
                    ELSE 2 
                END,
                last_reviewed ASC NULLS FIRST
        """

        params = topic_ids + type_filter
        rows = db.fetchall(query, params)
        return [Flashcard.from_row(row) for row in rows]

    def update_card_review_status(self, card_id: int, rating: int):
        card = self.get_card(card_id)
        if not card:
            return

        # Получаем порог из настроек
        threshold_row = db.fetchone("SELECT setting_value FROM app_settings WHERE setting_key = 'review_threshold'")
        threshold = int(threshold_row["setting_value"]) if threshold_row else 3

        if rating == 1 or rating == 2:
            new_status = "learning"
            new_consecutive = 0
        else:
            new_consecutive = card.consecutive_correct + 1
            if new_consecutive >= threshold:
                new_status = "review"
            else:
                new_status = card.review_status

        db.execute("""
            UPDATE flashcards 
            SET review_status = ?, consecutive_correct = ?, last_reviewed = datetime('now')
            WHERE id = ?
        """, (new_status, new_consecutive, card_id))

    def get_review_stats(self, topic_id: int = None) -> dict:
        """Возвращает статистику повторений по теме или всем темам"""
        if topic_id:
            query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN review_status = 'review' THEN 1 ELSE 0 END) as reviewed,
                    SUM(CASE WHEN review_status = 'learning' THEN 1 ELSE 0 END) as learning,
                    SUM(CASE WHEN review_status = 'new' THEN 1 ELSE 0 END) as new_cards
                FROM flashcards 
                WHERE topic_id = ? AND is_active = 1
            """
            row = db.fetchone(query, (topic_id,))
        else:
            query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN review_status = 'review' THEN 1 ELSE 0 END) as reviewed,
                    SUM(CASE WHEN review_status = 'learning' THEN 1 ELSE 0 END) as learning,
                    SUM(CASE WHEN review_status = 'new' THEN 1 ELSE 0 END) as new_cards
                FROM flashcards 
                WHERE is_active = 1
            """
            row = db.fetchone(query)

        if row:
            return {
                "total": row["total"] if isinstance(row, dict) else row[0],
                "reviewed": row["reviewed"] if isinstance(row, dict) else row[1],
                "learning": row["learning"] if isinstance(row, dict) else row[2],
                "new_cards": row["new_cards"] if isinstance(row, dict) else row[3]
            }
        return {"total": 0, "reviewed": 0, "learning": 0, "new_cards": 0}

    def deactivate_card(self, card_id: int, active: bool = False):
        """Включает/выключает карточку (не удаляет)"""
        db.execute("UPDATE flashcards SET is_active = ? WHERE id = ?", (1 if active else 0, card_id))