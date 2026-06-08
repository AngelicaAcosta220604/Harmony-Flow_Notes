# models/quick_note.py
"""
Быстрая запись, созданная во время фокус-сессии.
"""

class QuickNote:
    def __init__(self, id, session_id, topic_id, text, created_at):
        self.id = id
        self.session_id = session_id
        self.topic_id = topic_id
        self.text = text
        self.created_at = created_at

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            session_id=row["session_id"],
            topic_id=row["topic_id"],
            text=row["text"],
            created_at=row["created_at"]
        )
