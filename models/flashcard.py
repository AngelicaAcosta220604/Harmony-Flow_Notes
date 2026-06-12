# models/flashcard.py

# models/flashcard.py

from datetime import datetime


class Flashcard:
    def __init__(self, id=None, topic_id=None, source_note_id=None, type="free",
                 question=None, answer=None, content=None, created_at=None, updated_at=None,
                 review_status="new", consecutive_correct=0, last_reviewed=None, is_active=1):
        self.id = id
        self.topic_id = topic_id
        self.source_note_id = source_note_id  # ID заметки, из которой создана карточка
        self.type = type  # "free" или "qa"
        self.question = question
        self.answer = answer
        self.content = content  # для свободного типа
        self.created_at = created_at
        self.updated_at = updated_at

        # НОВЫЕ ПОЛЯ ДЛЯ ПОВТОРЕНИЯ
        self.review_status = review_status  # "new", "learning", "review"
        self.consecutive_correct = consecutive_correct  # сколько раз подряд "Знаю"
        self.last_reviewed = last_reviewed  # дата последнего повторения
        self.is_active = is_active  # 1 = активна, 0 = не актуально

    @classmethod
    def from_row(cls, row):
        """Создаёт объект Flashcard из строки БД (словарь или кортеж)"""
        # Если row — словарь
        if isinstance(row, dict):
            return cls(
                id=row.get("id"),
                topic_id=row.get("topic_id"),
                source_note_id=row.get("source_note_id"),
                type=row.get("type", "free"),
                question=row.get("question"),
                answer=row.get("answer"),
                content=row.get("content"),
                created_at=row.get("created_at"),
                updated_at=row.get("updated_at"),
                review_status=row.get("review_status", "new"),
                consecutive_correct=row.get("consecutive_correct", 0),
                last_reviewed=row.get("last_reviewed"),
                is_active=row.get("is_active", 1)
            )
        # Если row — кортеж (тут порядок важен)
        else:
            # Индексы зависят от порядка в SELECT
            # Базовые поля (первые 8)
            id_val = row[0] if len(row) > 0 else None
            topic_id_val = row[1] if len(row) > 1 else None
            source_note_id_val = row[2] if len(row) > 2 else None
            type_val = row[3] if len(row) > 3 else "free"
            question_val = row[4] if len(row) > 4 else None
            answer_val = row[5] if len(row) > 5 else None
            content_val = row[6] if len(row) > 6 else None
            created_at_val = row[7] if len(row) > 7 else None
            updated_at_val = row[8] if len(row) > 8 else None

            # Новые поля (если есть)
            review_status_val = row[9] if len(row) > 9 else "new"
            consecutive_correct_val = row[10] if len(row) > 10 else 0
            last_reviewed_val = row[11] if len(row) > 11 else None
            is_active_val = row[12] if len(row) > 12 else 1

            return cls(
                id=id_val,
                topic_id=topic_id_val,
                source_note_id=source_note_id_val,
                type=type_val,
                question=question_val,
                answer=answer_val,
                content=content_val,
                created_at=created_at_val,
                updated_at=updated_at_val,
                review_status=review_status_val,
                consecutive_correct=consecutive_correct_val,
                last_reviewed=last_reviewed_val,
                is_active=is_active_val
            )

    def to_dict(self):
        """Преобразует объект в словарь для БД"""
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "source_note_id": self.source_note_id,
            "type": self.type,
            "question": self.question,
            "answer": self.answer,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "review_status": self.review_status,
            "consecutive_correct": self.consecutive_correct,
            "last_reviewed": self.last_reviewed,
            "is_active": self.is_active
        }