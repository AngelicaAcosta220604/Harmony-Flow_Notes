# utils/local_time.py
"""
Legacy wrapper for TimeService.
TODO: Постепенно заменить прямые вызовы на TimeService.
"""

from services.time_service import TimeService


def now_local_iso() -> str:
    """Legacy: используйте TimeService.now_for_db()"""
    return TimeService.now_for_db()


def now_iso() -> str:
    """Legacy: используйте TimeService.now_iso()"""
    return TimeService.now_iso()


def format_display(db_time: str) -> str:
    """Legacy: используйте TimeService.format_display()"""
    return TimeService.format_display(db_time)


def now_datetime():
    """Legacy: используйте TimeService.now_datetime()"""
    return TimeService.now_datetime()