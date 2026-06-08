# utils/validators.py
"""
validators.py — модуль валидации данных.

Используется в контроллерах и UI:
- проверка названий тем
- проверка заметок
- проверка задач
- проверка карточек
- проверка дедлайнов
"""

from datetime import datetime


# ---------------------------------------------------------
# ТЕМЫ
# ---------------------------------------------------------

def validate_topic_name(name: str) -> bool:
    """Название темы должно быть непустым и не длиннее 100 символов."""
    if not name or not name.strip():
        return False
    return len(name.strip()) <= 100


# ---------------------------------------------------------
# ЗАМЕТКИ
# ---------------------------------------------------------

def validate_note_title(title: str) -> bool:
    """Заголовок заметки должен быть непустым."""
    return bool(title and title.strip())


def validate_note_content(content: str) -> bool:
    """Контент заметки может быть пустым, но не None."""
    return content is not None


# ---------------------------------------------------------
# ЗАДАЧИ
# ---------------------------------------------------------

def validate_task_title(title: str) -> bool:
    """Заголовок задачи обязателен."""
    return bool(title and title.strip())


def validate_deadline(deadline: str | None) -> bool:
    """
    Проверяет корректность дедлайна.
    Формат: ISO (YYYY-MM-DD HH:MM:SS)
    """
    if not deadline:
        return True  # дедлайн необязателен

    try:
        datetime.fromisoformat(deadline)
        return True
    except:
        return False


# ---------------------------------------------------------
# КАРТОЧКИ
# ---------------------------------------------------------

def validate_flashcard(question: str, answer: str | None = None, type: str = "free") -> bool:
    """Проверяет корректность карточки."""
    if not question or not question.strip():
        return False

    if type == "qa" and (not answer or not answer.strip()):
        return False

    return True


# ---------------------------------------------------------
# ОБЩИЕ
# ---------------------------------------------------------

def is_non_empty(value: str) -> bool:
    """Проверяет, что строка не пустая."""
    return bool(value and value.strip())
