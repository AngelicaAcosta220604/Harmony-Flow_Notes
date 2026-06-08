# managers/constants_manager.py
"""
ConstantsManager — единый центр хранения констант приложения.

Реализует:
- пути к ресурсам
- имена таблиц
- статусы задач
- типы карточек
- ключи настроек
- значения по умолчанию
- системные интервалы (autosave, ping, notifications)

Используется во всех модулях проекта.
"""

from pathlib import Path


class ConstantsManager:

    # ---------------------------------------------------------
    # ПУТИ
    # ---------------------------------------------------------
    ROOT = Path(__file__).resolve().parents[1]

    PATHS = {
        "database": ROOT / "database" / "app.db",
        "sounds": ROOT / "resources" / "sounds",
        "icons": ROOT / "resources" / "icons",
        "backups": ROOT / "backups",
        "exports": ROOT / "exports",
        "sync": ROOT / "sync",
    }

    # ---------------------------------------------------------
    # ТАБЛИЦЫ БД
    # ---------------------------------------------------------
    TABLES = {
        "topics": "topics",
        "notes": "notes",
        "tasks": "tasks",
        "flashcards": "flashcards",
        "sessions": "sessions",
        "session_logs": "session_state_logs",
        "quick_notes": "quick_notes",
        "settings": "settings",
    }

    # ---------------------------------------------------------
    # СТАТУСЫ ЗАДАЧ
    # ---------------------------------------------------------
    TASK_STATUS = {
        "active": "active",
        "done": "done",
        "overdue": "overdue",
    }

    # ---------------------------------------------------------
    # ТИПЫ КАРТОЧЕК
    # ---------------------------------------------------------
    FLASHCARD_TYPES = {
        "free": "free",
        "qa": "qa",
    }

    # ---------------------------------------------------------
    # КЛЮЧИ НАСТРОЕК
    # ---------------------------------------------------------
    SETTINGS_KEYS = {
        "volume": "volume",
        "sound": "sound",
        "session_length": "session_length",
        "autosave_delay": "autosave_delay",
        "theme": "theme",
    }

    # ---------------------------------------------------------
    # ЗНАЧЕНИЯ ПО УМОЛЧАНИЮ
    # ---------------------------------------------------------
    DEFAULTS = {
        "volume": "0.5",
        "sound": "rain",
        "session_length": "25",
        "autosave_delay": "800",
        "theme": "light",
    }

    # ---------------------------------------------------------
    # ИНТЕРВАЛЫ (мс)
    # ---------------------------------------------------------
    INTERVALS = {
        "autosave": 800,
        "ping_idle": 5 * 60 * 1000,
        "ping_timeout": 20 * 1000,
        "notifications_check": 60 * 1000,
    }

    # ---------------------------------------------------------
    # УТИЛИТЫ
    # ---------------------------------------------------------
    @classmethod
    def get_path(cls, key: str):
        return cls.PATHS.get(key)

    @classmethod
    def get_default(cls, key: str):
        return cls.DEFAULTS.get(key)

    @classmethod
    def get_setting_key(cls, key: str):
        return cls.SETTINGS_KEYS.get(key)
# Константы (интервалы, статусы, типы)