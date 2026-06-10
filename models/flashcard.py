# models/flashcard.py

class Flashcard:
    def __init__(self, id=None, topic_id=None, source_note_id=None, type="free",
                 question=None, answer=None, content=None, created_at=None):
        self.id = id
        self.topic_id = topic_id
        self.source_note_id = source_note_id  # ID заметки, из которой создана карточка
        self.type = type  # "free" или "qa"
        self.question = question
        self.answer = answer
        self.content = content  # для свободного типа
        self.created_at = created_at

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row.get("id"),
            topic_id=row.get("topic_id"),
            source_note_id=row.get("source_note_id"),
            type=row.get("type", "free"),
            question=row.get("question"),
            answer=row.get("answer"),
            content=row.get("content"),
            created_at=row.get("created_at")
        )