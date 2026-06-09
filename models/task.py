# models/task.py
class Task:
    def __init__(self, id: int = None, topic_id: int = None, title: str = "",
                 description: str = "", deadline: str = None, status: str = "active",
                 created_at: str = None, completed_at: str = None):
        self.id = id
        self.topic_id = topic_id
        self.title = title
        self.description = description
        self.deadline = deadline
        self.status = status
        self.created_at = created_at
        self.completed_at = completed_at

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id=row.get("id"),
            topic_id=row.get("topic_id"),
            title=row.get("title", ""),
            description=row.get("description", ""),
            deadline=row.get("deadline"),
            status=row.get("status", "active"),
            created_at=row.get("created_at"),
            completed_at=row.get("completed_at")
        )