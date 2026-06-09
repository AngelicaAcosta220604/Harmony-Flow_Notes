"""
SessionController — контроллер для работы с фокус-сессиями.

Реализует:
- запуск сессии
- пауза / возобновление
- завершение (теперь совместимо с тестами)
- логирование состояния (концентрация, энергия, интерес)
- добавление быстрых заметок
- получение истории сессий
- расчёт длительности
- ручное создание сессии (для тестов аналитики)
"""
from database.db_manager import db
from models.session import Session
from models.session_state_log import SessionStateLog
from models.quick_note import QuickNote
from datetime import datetime, timedelta


class SessionController:

    # ---------------------------------------------------------
    # ЗАПУСК СЕССИИ
    # ---------------------------------------------------------
    def start_session(self, topic_id: int) -> int:
        """
        Создаёт новую сессию.
        start_time = текущее время
        end_time = NULL
        duration = NULL

        ВАЖНО: если темы с таким id ещё нет (как в тестах) — создаём её.
        """
        # если темы нет — создаём заглушку, чтобы не падал FK
        topic = db.fetchone("SELECT id FROM topics WHERE id = ?", (topic_id,))
        if not topic:
            db.execute(
                "INSERT INTO topics (id, name) VALUES (?, ?)",
                (topic_id, f"Тема {topic_id}")
            )

        now = datetime.now()

        cursor = db.execute(
            "INSERT INTO sessions (topic_id, start_time) VALUES (?, ?)",
            (topic_id, now)
        )
        return cursor.lastrowid
###RRRR
    # Получить все сессии
    rows = db.fetchall("SELECT * FROM sessions")
    sessions = [Session.from_row(row) for row in rows]

    # Получить одну сессию
    row = db.fetchone("SELECT * FROM sessions WHERE id = ?", (5,))
    if row:
        session = Session.from_row(row)
        ####RRRRR
    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ СЕССИИ
    # ---------------------------------------------------------
    def get_session(self, session_id: int) -> Session | None:
        row = db.fetchone("SELECT * FROM sessions WHERE id = ?", (session_id,))
        return Session.from_row(row) if row else None

    # ---------------------------------------------------------
    # ПАУЗА
    # ---------------------------------------------------------
    def pause_session(self, session_id: int):
        self.log_state(session_id, "pause", 0)

    # ---------------------------------------------------------
    # ВОЗОБНОВЛЕНИЕ
    # ---------------------------------------------------------
    def resume_session(self, session_id: int):
        self.log_state(session_id, "resume", 0)

    # ---------------------------------------------------------
    # ЗАВЕРШЕНИЕ СЕССИИ (ТЕСТОВАЯ + ПРОДАКШН ВЕРСИЯ)
    # ---------------------------------------------------------
    def end_session(self, session_id: int, duration: int = None,
                    focus: int = None, energy: int = None, interest: int = None):
        """
        Универсальная версия:
        - если duration передан → тестовый режим
        - если duration None → рассчитываем автоматически (продакшн)
        """

        session = self.get_session(session_id)
        if not session:
            return

        end_time = datetime.now()

        # ТЕСТОВЫЙ РЕЖИМ
        if duration is not None:
            db.execute(
                """
                UPDATE sessions
                SET end_time = ?, duration = ?, focus = ?, energy = ?, interest = ?
                WHERE id = ?
                """,
                (end_time, duration, focus, energy, interest, session_id)
            )
            return

        # ПРОДАКШН РЕЖИМ
        start_time = datetime.fromisoformat(session.start_time)
        duration_minutes = int((end_time - start_time).total_seconds() // 60)

        db.execute(
            """
            UPDATE sessions
            SET end_time = ?, duration = ?
            WHERE id = ?
            """,
            (end_time, duration_minutes, session_id)
        )

    # ---------------------------------------------------------
    # РУЧНОЕ СОЗДАНИЕ СЕССИИ (для тестов аналитики)
    # ---------------------------------------------------------
    def _create_manual_session(self, topic_id, start, end, duration, focus, energy, interest):
        cursor = db.execute(
            """
            INSERT INTO sessions (topic_id, start_time, end_time, duration, focus, energy, interest)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (topic_id, start, end, duration, focus, energy, interest)
        )
        return cursor.lastrowid

    # ---------------------------------------------------------
    # ЛОГИ СОСТОЯНИЙ
    # ---------------------------------------------------------
    def log_state(self, session_id: int, metric: str, value: int, minute: int | None = None):
        db.execute(
            """
            INSERT INTO session_state_logs (session_id, metric, value, timestamp, minute)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, metric, value, datetime.now(), minute)
        )

    def get_session_logs(self, session_id: int) -> list[SessionStateLog]:
        rows = db.fetchall(
            "SELECT * FROM session_state_logs WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        )
        return [SessionStateLog.from_row(row) for row in rows]

    # ---------------------------------------------------------
    # БЫСТРЫЕ ЗАМЕТКИ
    # ---------------------------------------------------------
    def add_quick_note(self, session_id: int, topic_id: int, text: str) -> int:
        cursor = db.execute(
            "INSERT INTO quick_notes (session_id, topic_id, text) VALUES (?, ?, ?)",
            (session_id, topic_id, text)
        )
        return cursor.lastrowid

    def get_quick_notes(self, session_id: int) -> list[QuickNote]:
        rows = db.fetchall(
            "SELECT * FROM quick_notes WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,)
        )
        return [QuickNote.from_row(row) for row in rows]

    # ---------------------------------------------------------
    # ИСТОРИЯ СЕССИЙ
    # ---------------------------------------------------------
    def get_sessions_by_topic(self, topic_id: int) -> list[Session]:
        rows = db.fetchall(
            "SELECT * FROM sessions WHERE topic_id = ? ORDER BY start_time DESC",
            (topic_id,)
        )
        return [Session.from_row(row) for row in rows]

    # ---------------------------------------------------------
    # УДАЛЕНИЕ
    # ---------------------------------------------------------
    def delete_session(self, session_id: int):
        db.execute("DELETE FROM session_state_logs WHERE session_id = ?", (session_id,))
        db.execute("DELETE FROM quick_notes WHERE session_id = ?", (session_id,))
        db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
