class Session:
    def __init__(self, id, topic_id, start_time, end_time=None,
                 duration_minutes=None, status='active', created_at=None,
                 total_active_seconds=0):  # ← добавить
        self.id = id
        self.topic_id = topic_id
        self.start_time = start_time
        self.end_time = end_time
        self.duration_minutes = duration_minutes
        self.status = status
        self.created_at = created_at
        self.total_active_seconds = total_active_seconds  # ← добавить

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row['id'],
            topic_id=row['topic_id'],
            start_time=row['start_time'],
            end_time=row.get('end_time'),
            duration_minutes=row.get('duration_minutes'),
            status=row.get('status', 'active'),
            created_at=row.get('created_at'),
            total_active_seconds=row.get('total_active_seconds', 0)  # ← добавить
        )