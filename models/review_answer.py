# models/review_answer.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class ReviewAnswer:
    """Модель ответа в сессии повторения"""
    id: Optional[int] = None
    session_id: int = 0
    card_id: int = 0
    rating: int = 0  # 1=забыл, 2=слабо, 3=знаю
    response_time_seconds: int = 0

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row[0],
            session_id=row[1],
            card_id=row[2],
            rating=row[3],
            response_time_seconds=row[4]
        )