# models/flashcard.py
"""
Модель карточки.
Тип: 'free' или 'qa' (вопрос-ответ).
"""

class Flashcard:
    def __init__(self, id, topic_id, question, answer, type):
        self.id = id
        self.topic_id = topic_id
        self.question = question
        self.answer = answer
        self.type = type

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            topic_id=row["topic_id"],
            question=row["question"],
            answer=row["answer"],
            type=row["type"]
        )
