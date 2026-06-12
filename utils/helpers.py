# Вспомогательные функции
# utils/helpers.py
"""
helpers.py — набор универсальных вспомогательных функций.

Используется по всему проекту:
- форматирование дат
- безопасная работа с файлами
- генерация UUID
- нормализация строк
- создание сниппетов
- конвертация datetime
"""

from __future__ import annotations
from datetime import datetime
from pathlib import Path
import uuid
import re
import time

# ---------------------------------------------------------
# ДАТЫ И ВРЕМЯ
# ---------------------------------------------------------

def now_iso() -> str:
    """Возвращает текущее время в ISO-формате."""
    return datetime.now().isoformat()


def to_iso(dt: datetime) -> str:
    """Преобразует datetime → ISO строку."""
    return dt.isoformat()


def from_iso(s: str) -> datetime:
    """Преобразует ISO строку → datetime."""
    return datetime.fromisoformat(s)


def format_datetime(dt: datetime, fmt: str = "%d.%m.%Y %H:%M") -> str:
    """Форматирует datetime в строку."""
    return dt.strftime(fmt)


# ---------------------------------------------------------
# ФАЙЛЫ
# ---------------------------------------------------------

def safe_read(path: str | Path, default: str = "") -> str:
    """
    Безопасно читает файл.
    Если файла нет — возвращает default.
    """
    p = Path(path)
    if not p.exists():
        return default
    return p.read_text(encoding="utf-8")


def safe_write(path: str | Path, text: str):
    """
    Безопасно записывает файл, создавая папки при необходимости.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


# ---------------------------------------------------------
# СТРОКИ
# ---------------------------------------------------------

def normalize(s: str) -> str:
    """
    Нормализует строку:
    - убирает лишние пробелы
    - заменяет множественные пробелы на один
    - убирает переносы строк по краям
    """
    if not s:
        return ""
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s


def snippet(text: str, query: str, radius: int = 40) -> str | None:
    """
    Создаёт сниппет вокруг найденного слова.
    Используется в поиске.
    """
    if not text:
        return None

    text_lower = text.lower()
    q = query.lower()

    index = text_lower.find(q)
    if index == -1:
        return None

    start = max(0, index - radius)
    end = min(len(text), index + len(query) + radius)

    return text[start:end].replace("\n", " ") + "..."


# ---------------------------------------------------------
# UUID
# ---------------------------------------------------------

def generate_id() -> str:
    """Генерирует UUID4 как строку."""
    return str(uuid.uuid4())


# ---------------------------------------------------------
# ПРОВЕРКИ
# ---------------------------------------------------------

def is_empty(value) -> bool:
    """Проверяет, является ли значение пустым."""
    return value is None or value == "" or (isinstance(value, str) and value.strip() == "")


def coalesce(*values):
    """
    Возвращает первое непустое значение.
    Пример:
        coalesce(None, "", "hello") → "hello"
    """
    for v in values:
        if not is_empty(v):
            return v
    return None


# ---------------------------------------------------------
# UI УТИЛИТЫ
# ---------------------------------------------------------

def shorten(text: str, max_len: int = 40) -> str:
    """
    Обрезает текст для отображения в UI.
    """
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."

# ---------------------------------------------------------
# Время
# ---------------------------------------------------------


