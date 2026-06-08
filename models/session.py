# models/session.py
"""
Модель фокус-сессии.
Хранит время начала, окончания, длительность и показатели состояния.
"""

from dataclasses import dataclass


@dataclass
class Session:
    id: int
    topic_id: int
    start_time: str
    end_time: str | None
    duration: int | None
    focus: int | None
    energy: int | None
    interest: int | None

    @classmethod
    def from_row(cls, row):
        if not row:
            return None

        return cls(
            id=row["id"],
            topic_id=row["topic_id"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            duration=row["duration"],
            focus=row["focus"],
            energy=row["energy"],
            interest=row["interest"]
        )
