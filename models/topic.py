# models/topic.py
class Topic:
    def __init__(self, id: int = None, name: str = "", description: str = "",
                 parent_id: int = None, type: str = "topic",
                 created_at: str = None, updated_at: str = None):
        self.id = id
        self.name = name
        self.description = description
        self.parent_id = parent_id
        self.type = type
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id=row.get("id"),
            name=row.get("name", ""),
            description=row.get("description", ""),
            parent_id=row.get("parent_id"),
            type=row.get("type", "topic"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at")
        )

    def __repr__(self):
        return f"<Topic {self.id}: {self.name}>"