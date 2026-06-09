# models/quick_note.py
class QuickNote:
    def __init__(self, id: int = None, session_id: int = None, topic_id: int = None,
                 content: str = "", created_at: str = None):
        self.id = id
        self.session_id = session_id
        self.topic_id = topic_id
        self.content = content
        self.created_at = created_at

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id=row.get("id"),
            session_id=row.get("session_id"),
            topic_id=row.get("topic_id"),
            content=row.get("content", ""),
            created_at=row.get("created_at")
        )