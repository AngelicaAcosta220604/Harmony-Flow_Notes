# models/session_state_log.py
"""
Лог изменения состояния пользователя во время сессии.
metric: concentration / energy / interest
"""

class SessionStateLog:
    def __init__(self, id, session_id, metric, value, timestamp, minute):
        self.id = id
        self.session_id = session_id
        self.metric = metric
        self.value = value
        self.timestamp = timestamp
        self.minute = minute

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            session_id=row["session_id"],
            metric=row["metric"],
            value=row["value"],
            timestamp=row["timestamp"],
            minute=row["minute"]
        )
