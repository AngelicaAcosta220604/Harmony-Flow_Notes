# models/review_session.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ReviewSession:
    """Модель сессии повторения"""
    id: Optional[int] = None
    session_date: Optional[datetime] = None
    total_cards: int = 0
    completed_cards: int = 0
    duration_minutes: int = 0

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row[0],
            session_date=datetime.fromisoformat(row[1]) if row[1] else None,
            total_cards=row[2],
            completed_cards=row[3],
            duration_minutes=row[4]
        )