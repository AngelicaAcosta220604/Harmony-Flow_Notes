# models/topic.py
"""
Модель темы (папки или подтемы).
Используется для структуры знаний.
"""

class Topic:
    def __init__(self, id, parent_id, name, created_at):
        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.created_at = created_at

    @classmethod
    def from_row(cls, row):
        """Создание объекта из sqlite3.Row"""
        return cls(
            id=row["id"],
            parent_id=row["parent_id"],
            name=row["name"],
            created_at=row["created_at"]
        )# models/topic.py
"""
Модель темы (папки или подтемы).
Используется для структуры знаний.
"""

class Topic:
    def __init__(self, id, parent_id, name, created_at):
        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.created_at = created_at

    @classmethod
    def from_row(cls, row):
        """Создание объекта из sqlite3.Row"""
        return cls(
            id=row["id"],
            parent_id=row["parent_id"],
            name=row["name"],
            created_at=row["created_at"]
        )