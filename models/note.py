# models/note.py
class Note:
    def __init__(self, id: int = None, topic_id: int = None, title: str = "",
                 content: str = "", created_at: str = None, updated_at: str = None):
        self.id = id
        self.topic_id = topic_id
        self.title = title
        self.content = content
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id=row.get("id"),
            topic_id=row.get("topic_id"),
            title=row.get("title", ""),
            content=row.get("content", ""),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at")
        )