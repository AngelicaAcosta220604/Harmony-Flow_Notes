from datetime import datetime
from typing import Optional


class TimeService:
    """Единый сервис для работы со временем во всём приложении."""

    @staticmethod
    def now_for_db() -> str:
        """Текущее время для сохранения в БД (локальное)."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def now_iso() -> str:
        """Текущее время в ISO формате."""
        return datetime.now().isoformat(timespec='seconds')

    @staticmethod
    def format_display(db_time: Optional[str]) -> str:
        """Конвертирует время из БД в читаемый формат для UI."""
        if not db_time:
            return ""

        try:
            clean_time = db_time.replace('T', ' ')
            dt = datetime.fromisoformat(clean_time)
            return dt.strftime("%d.%m.%Y %H:%M")
        except Exception:
            return db_time[:16] if len(db_time) > 16 else db_time

    @staticmethod
    def format_date(db_time: Optional[str]) -> str:
        """Только дата для отображения."""
        if not db_time:
            return ""

        try:
            clean_time = db_time.replace('T', ' ')
            dt = datetime.fromisoformat(clean_time)
            return dt.strftime("%d.%m.%Y")
        except Exception:
            return db_time[:10] if len(db_time) > 10 else db_time

    @staticmethod
    def now_datetime() -> datetime:
        """Текущее время как объект datetime."""
        return datetime.now()