# models/task.py
"""
Модель задачи.
Содержит дедлайн, статус и описание.
"""

class Task:
    def __init__(self, id, topic_id, title, description, created_at, deadline, status):
        self.id = id
        self.topic_id = topic_id
        self.title = title
        self.description = description
        self.created_at = created_at
        self.deadline = deadline
        self.status = status

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            topic_id=row["topic_id"],
            title=row["title"],
            description=row["description"],
            created_at=row["created_at"],
            deadline=row["deadline"],
            status=row["status"]
        )
