# utils/db_time.py
"""
Функции для работы с временем в базе данных.
Используют локальное время вместо SQLite datetime('now').
"""

from datetime import datetime


def db_now() -> str:
    """
    Возвращает текущее локальное время в формате ISO для SQLite.
    """
    return datetime.now().isoformat(timespec='seconds')


def db_now_datetime() -> datetime:
    """
    Возвращает текущее локальное время как объект datetime.
    """
    return datetime.now()