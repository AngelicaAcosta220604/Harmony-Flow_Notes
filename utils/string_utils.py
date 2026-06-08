# utils/string_utils.py
"""
string_utils.py — расширенные функции для работы со строками.

Реализует:
- продвинутую нормализацию
- очистку HTML
- транслитерацию
- генерацию slug
- fuzzy matching
- сравнение строк
- извлечение ключевых слов
- разбиение текста на предложения
"""

import re
import unicodedata
from difflib import SequenceMatcher


# ---------------------------------------------------------
# НОРМАЛИЗАЦИЯ
# ---------------------------------------------------------

def normalize_spaces(text: str) -> str:
    """Убирает лишние пробелы, табы, переносы."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def normalize_text(text: str) -> str:
    """Полная нормализация: пробелы, unicode, нижний регистр."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = normalize_spaces(text)
    return text.lower()


# ---------------------------------------------------------
# HTML ОЧИСТКА
# ---------------------------------------------------------

def strip_html(text: str) -> str:
    """Удаляет HTML-теги."""
    return re.sub(r"<[^>]+>", "", text or "").strip()


# ---------------------------------------------------------
# ТРАНСЛИТЕРАЦИЯ
# ---------------------------------------------------------

def translit(text: str) -> str:
    """Транслитерация русского → латиница."""
    mapping = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d",
        "е": "e", "ё": "yo", "ж": "zh", "з": "z", "и": "i",
        "й": "y", "к": "k", "л": "l", "м": "m", "н": "n",
        "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
        "у": "u", "ф": "f", "х": "h", "ц": "ts", "ч": "ch",
        "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "",
        "э": "e", "ю": "yu", "я": "ya",
    }
    result = ""
    for ch in text.lower():
        result += mapping.get(ch, ch)
    return result


# ---------------------------------------------------------
# SLUG
# ---------------------------------------------------------

def slugify(text: str) -> str:
    """Создаёт URL-friendly slug."""
    text = translit(text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


# ---------------------------------------------------------
# СРАВНЕНИЕ СТРОК
# ---------------------------------------------------------

def similarity(a: str, b: str) -> float:
    """Возвращает коэффициент похожести строк (0–1)."""
    return SequenceMatcher(None, a, b).ratio()


def is_similar(a: str, b: str, threshold: float = 0.75) -> bool:
    """Проверяет, похожи ли строки."""
    return similarity(a, b) >= threshold


# ---------------------------------------------------------
# FUZZY MATCHING
# ---------------------------------------------------------

def fuzzy_find(query: str, items: list[str], threshold: float = 0.6) -> list[str]:
    """
    Возвращает элементы списка, похожие на запрос.
    Используется в поиске.
    """
    result = []
    for item in items:
        if is_similar(query.lower(), item.lower(), threshold):
            result.append(item)
    return result


# ---------------------------------------------------------
# РАЗБИЕНИЕ ТЕКСТА
# ---------------------------------------------------------

def split_sentences(text: str) -> list[str]:
    """Разбивает текст на предложения."""
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


# ---------------------------------------------------------
# КЛЮЧЕВЫЕ СЛОВА
# ---------------------------------------------------------

def extract_keywords(text: str, min_len: int = 4) -> list[str]:
    """
    Извлекает ключевые слова:
    - убирает стоп-слова
    - нормализует
    - фильтрует короткие слова
    """
    if not text:
        return []

    stopwords = {
        "и", "в", "на", "по", "к", "с", "за", "от", "до",
        "что", "это", "как", "для", "или", "но", "а",
    }

    words = re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9]+", text.lower())
    return [w for w in words if len(w) >= min_len and w not in stopwords]
