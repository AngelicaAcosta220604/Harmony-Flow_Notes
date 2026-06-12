# database/db_manager.py
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Путь к базе данных (файл создастся в корне проекта)
DB_PATH = "hflow.db"


class DatabaseManager:
    """Менеджер для работы с SQLite базой данных."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Возвращает подключение к БД с row_factory = dict для удобства."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        """Создаёт все таблицы, если их нет."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # topics (папки и темы)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    parent_id INTEGER,
                    type TEXT DEFAULT 'topic',
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES topics (id)
                )
            """)

            # notes (заметки)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_id INTEGER NOT NULL,
                    title TEXT,
                    content TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    FOREIGN KEY (topic_id) REFERENCES topics (id)
                )
            """)

            # flashcards (карточки)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flashcards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_id INTEGER NOT NULL,
                    source_note_id INTEGER,
                    type TEXT DEFAULT 'free',
                    question TEXT,
                    answer TEXT,
                    content TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    review_status TEXT DEFAULT 'new',
                    consecutive_correct INTEGER DEFAULT 0,
                    last_reviewed TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (topic_id) REFERENCES topics (id),
                    FOREIGN KEY (source_note_id) REFERENCES notes (id)
                )
            """)

            # review_sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS review_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_date DATETIME NOT NULL,
                    total_cards INTEGER DEFAULT 0,
                    completed_cards INTEGER DEFAULT 0,
                    duration_minutes INTEGER DEFAULT 0
                )
            """)

            # review_answers
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS review_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    card_id INTEGER NOT NULL,
                    rating INTEGER NOT NULL,
                    response_time_seconds INTEGER DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES review_sessions(id) ON DELETE CASCADE,
                    FOREIGN KEY (card_id) REFERENCES flashcards(id) ON DELETE CASCADE
                )
            """)

            # tasks (задачи)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_id INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    deadline TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (topic_id) REFERENCES topics (id)
                )
            """)

            # sessions (сессии) — С ДОБАВЛЕННОЙ КОЛОНКОЙ total_active_seconds
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_id INTEGER NOT NULL,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_minutes INTEGER,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP,
                    total_active_seconds INTEGER DEFAULT 0,
                    FOREIGN KEY (topic_id) REFERENCES topics (id)
                )
            """)

            # session_state_logs (логи концентрации/энергии/интереса)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_state_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    metric TEXT NOT NULL,
                    value INTEGER NOT NULL,
                    minute INTEGER,
                    created_at TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)

            # quick_notes (быстрые записи)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quick_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    topic_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id),
                    FOREIGN KEY (topic_id) REFERENCES topics (id)
                )
            """)

            # app_settings (настройки)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL
                )
            """)

            # Добавляем колонку total_active_seconds для существующих БД (миграция)
            cursor.execute("PRAGMA table_info(sessions)")
            existing_columns = [col[1] for col in cursor.fetchall()]
            if 'total_active_seconds' not in existing_columns:
                cursor.execute("ALTER TABLE sessions ADD COLUMN total_active_seconds INTEGER DEFAULT 0")

            # Добавляем настройки по умолчанию, если их нет
            default_settings = [
                ("user_name", "Пользователь"),
                ("theme", "light"),
                ("activity_check_interval_minutes", "15"),
                ("auto_pause_minutes", "10"),
                ("auto_save_interval_seconds", "60"),
                ("notifications_enabled", "true"),
                ("default_sound", "off"),
                ("review_threshold", "3"),
            ]
            for key, value in default_settings:
                cursor.execute("""
                    INSERT OR IGNORE INTO app_settings (setting_key, setting_value)
                    VALUES (?, ?)
                """, (key, value))

            conn.commit()

    # ---------------------------------------------------------
    # УНИВЕРСАЛЬНЫЕ МЕТОДЫ ДЛЯ ЗАПРОСОВ
    # ---------------------------------------------------------

    def fetchall(self, query: str, params: tuple = ()) -> List[Dict]:
        """Выполняет SELECT и возвращает список словарей."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Выполняет SELECT и возвращает один словарь."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    def execute(self, query: str, params: tuple = ()) -> int:
        """Выполняет INSERT/UPDATE/DELETE и возвращает lastrowid."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Выполняет INSERT и возвращает lastrowid (алиас для execute)."""
        return self.execute(query, params)

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Выполняет UPDATE/DELETE и возвращает количество изменённых строк."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

    def executemany(self, query: str, params_list: List[tuple]) -> None:
        """Выполняет массовую вставку (например, для тестов)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()


# Глобальный экземпляр для всего приложения (один объект на всё)
db = DatabaseManager()