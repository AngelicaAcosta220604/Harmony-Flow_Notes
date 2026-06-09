# models/session.py
class Session:
    def __init__(self, id: int = None, topic_id: int = None, start_time: str = None,
                 end_time: str = None, duration: int = None, focus: int = None,
                 status: str = "active", created_at: str = None):
        self.id = id
        self.topic_id = topic_id
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration  # minutes
        self.focus = focus       # средняя концентрация (опционально)
        self.status = status
        self.created_at = created_at

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id=row.get("id"),
            topic_id=row.get("topic_id"),
            start_time=row.get("start_time"),
            end_time=row.get("end_time"),
            duration=row.get("duration_minutes"),
            focus=row.get("focus"),
            status=row.get("status", "active"),
            created_at=row.get("created_at")
        )