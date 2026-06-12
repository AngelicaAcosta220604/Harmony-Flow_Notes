# utils/local_time.py

from datetime import datetime
import pytz


def now_local_iso() -> str:
    """
    Возвращает текущее локальное время в ISO-формате.
    Автоматически определяет локальный часовой пояс.
    """
    # Получаем локальный часовой пояс
    local_tz = datetime.now().astimezone().tzinfo

    # Текущее время в локальном поясе
    local_time = datetime.now(local_tz)

    return local_time.isoformat(timespec='seconds')


def today_local() -> str:
    """
    Возвращает текущую локальную дату в формате YYYY-MM-DD.
    """
    local_tz = datetime.now().astimezone().tzinfo
    local_time = datetime.now(local_tz)
    return local_time.strftime("%Y-%m-%d")


def parse_local_datetime(date_string: str) -> datetime:
    """
    Парсит ISO строку в datetime с учётом локального часового пояса.
    Если строка без часового пояса, добавляет локальный.
    """
    dt = datetime.fromisoformat(date_string)

    # Если datetime без часового пояса, добавляем локальный
    if dt.tzinfo is None:
        local_tz = datetime.now().astimezone().tzinfo
        dt = dt.replace(tzinfo=local_tz)

    return dt


def format_local_time(dt: datetime = None, format_string: str = "%d.%m.%Y %H:%M:%S") -> str:
    """
    Форматирует datetime в локальное время.
    Если dt не указано - использует текущее время.
    """
    if dt is None:
        dt = datetime.now()

    # Если datetime без часового пояса, добавляем локальный
    if dt.tzinfo is None:
        local_tz = datetime.now().astimezone().tzinfo
        dt = dt.replace(tzinfo=local_tz)

    # Конвертируем в локальное время
    local_dt = dt.astimezone()

    return local_dt.strftime(format_string)