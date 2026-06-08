# models/note.py
"""
Модель заметки.
Поддерживает заголовок, текст, дату создания и обновления.
"""

class Note:
    def __init__(self, id, topic_id, title, content, created_at, updated_at):
        self.id = id
        self.topic_id = topic_id
        self.title = title
        self.content = content
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            topic_id=row["topic_id"],
            title=row["title"],
            content=row["content"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )