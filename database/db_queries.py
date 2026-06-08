# database/db_queries.py
"""
Этот файл содержит SQL-команды для создания всех таблиц,
которые описаны в техническом задании HFlow.

Переменная INIT_QUERIES — это список SQL-строк.
db_manager.init_db() проходит по ним и создаёт таблицы.
"""

INIT_QUERIES = [

    # ---------------------------------------------------------
    # 1. Таблица тем (папки + темы)
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_id INTEGER,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,

    # ---------------------------------------------------------
    # 2. Таблица заметок
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER,
        title TEXT NOT NULL,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,

    # ---------------------------------------------------------
    # 3. Таблица задач
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        deadline TIMESTAMP,
        status TEXT DEFAULT 'active'
    );
    """,

    # ---------------------------------------------------------
    # 4. Таблица карточек
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER,
        question TEXT,
        answer TEXT,
        type TEXT NOT NULL
    );
    """,

    # ---------------------------------------------------------
    # 5. Таблица фокус-сессий
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    duration INTEGER,
    focus INTEGER,
    energy INTEGER,
    interest INTEGER,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

    """,

    # ---------------------------------------------------------
    # 6. Таблица логов состояния (концентрация/энергия/интерес)
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS session_state_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        metric TEXT NOT NULL,
        value INTEGER NOT NULL,
        timestamp TIMESTAMP,
        minute INTEGER
    );
    """,

    # ---------------------------------------------------------
    # 7. Таблица быстрых записей
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS quick_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        topic_id INTEGER,
        text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,

    # ---------------------------------------------------------
    # 8. Таблица настроек приложения
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """
]
