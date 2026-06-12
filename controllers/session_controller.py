# controllers/session_controller.py

from database.db_manager import db
from models.session import Session
from models.session_state_log import SessionStateLog
from models.quick_note import QuickNote
from datetime import datetime
from PySide6.QtCore import QObject, Signal
from controllers.topic_controller import TopicController
from utils.local_time import now_local_iso


class SessionController(QObject):
    ping_needed = Signal()
    session_auto_paused = Signal(int)

    def _update_topic_timestamp(self, topic_id: int):
        TopicController().update_timestamp(topic_id)

    def __init__(self):
        super().__init__()
        self.ping_manager = None
        self.current_session_id = None
        self.is_active = False
        self.session_start_time = None  # Для отслеживания начала активного отрезка

    def set_ping_manager(self, ping_manager):
        self.ping_manager = ping_manager
        if self.ping_manager:
            self.ping_manager.pingNeeded.connect(self._on_ping_needed)
            self.ping_manager.timeoutReached.connect(self._on_ping_timeout)

    def _on_ping_needed(self):
        if self.is_active and self.current_session_id:
            self.ping_needed.emit()

    def _on_ping_timeout(self):
        if self.is_active and self.current_session_id:
            self.auto_pause_session()

    def auto_pause_session(self):
        if self.current_session_id:
            # Сохраняем активное время перед авто-паузой
            if self.is_active and self.session_start_time:
                elapsed = int((datetime.now() - self.session_start_time).total_seconds())
                db.execute(
                    "UPDATE sessions SET total_active_seconds = total_active_seconds + ? WHERE id = ?",
                    (elapsed, self.current_session_id)
                )
                self.session_start_time = None

            db.execute(
                "UPDATE sessions SET status = ? WHERE id = ?",
                ('auto_paused', self.current_session_id)
            )
            self.is_active = False
            self.session_auto_paused.emit(self.current_session_id)

    def user_responded_to_ping(self):
        if self.ping_manager:
            self.ping_manager.user_confirmed()

    def start_session(self, topic_id: int) -> int:
        topic = db.fetchone("SELECT id FROM topics WHERE id = ?", (topic_id,))
        if not topic:
            db.execute(
                "INSERT INTO topics (id, name) VALUES (?, ?)",
                (topic_id, f"Тема {topic_id}")
            )

        now = now_local_iso()

        session_id = db.execute(
            "INSERT INTO sessions (topic_id, start_time, status, total_active_seconds) VALUES (?, ?, ?, ?)",
            (topic_id, now, 'active', 0)
        )

        self.current_session_id = session_id
        self.is_active = True
        self.session_start_time = datetime.now()

        if self.ping_manager:
            self.ping_manager.reset_idle()

        self._update_topic_timestamp(topic_id)
        return self.current_session_id

    def get_session(self, session_id: int):
        row = db.fetchone("SELECT * FROM sessions WHERE id = ?", (session_id,))
        return Session.from_row(row) if row else None

    def pause_session(self, session_id: int):
        # Сохраняем активное время перед паузой
        if self.is_active and self.session_start_time:
            elapsed = int((datetime.now() - self.session_start_time).total_seconds())
            db.execute(
                "UPDATE sessions SET total_active_seconds = total_active_seconds + ? WHERE id = ?",
                (elapsed, session_id)
            )
            self.session_start_time = None

        db.execute(
            "UPDATE sessions SET status = ? WHERE id = ?",
            ('paused', session_id)
        )
        self.is_active = False

        if self.ping_manager:
            self.ping_manager.idle_timer.stop()
            self.ping_manager.timeout_timer.stop()

    def resume_session(self, session_id: int):
        db.execute(
            "UPDATE sessions SET status = ? WHERE id = ?",
            ('active', session_id)
        )
        self.is_active = True
        self.session_start_time = datetime.now()  # Запоминаем время возобновления

        if self.ping_manager:
            self.ping_manager.reset_idle()

    def end_session(self, session_id: int, duration: int = None):
        session = self.get_session(session_id)
        topic_id = session.topic_id if session else None
        if not session:
            return

        end_time = now_local_iso()

        # Добавляем последний активный отрезок
        if self.is_active and self.session_start_time:
            elapsed = int((datetime.now() - self.session_start_time).total_seconds())
            db.execute(
                "UPDATE sessions SET total_active_seconds = total_active_seconds + ? WHERE id = ?",
                (elapsed, session_id)
            )
            self.session_start_time = None

        # Получаем общее активное время
        updated_session = self.get_session(session_id)
        total_seconds = updated_session.total_active_seconds if updated_session else 0
        duration_minutes = total_seconds // 60

        db.execute(
            """
            UPDATE sessions
            SET end_time = ?, duration_minutes = ?, status = ?
            WHERE id = ?
            """,
            (end_time, duration_minutes, 'completed', session_id)
        )

        self.is_active = False
        self.current_session_id = None
        self.session_start_time = None

        if self.ping_manager:
            self.ping_manager.idle_timer.stop()
            self.ping_manager.timeout_timer.stop()

        if topic_id:
            self._update_topic_timestamp(topic_id)

    def log_state(self, session_id: int, metric: str, value: int, minute: int = None):
        if self.ping_manager and self.is_active:
            self.ping_manager.reset_idle()

        now = datetime.now().isoformat()

        db.execute(
            """
            INSERT INTO session_state_logs (session_id, metric, value, created_at, minute)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, metric, value, now, minute)
        )

    def get_session_logs(self, session_id: int):
        rows = db.fetchall(
            "SELECT * FROM session_state_logs WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        )
        return [SessionStateLog.from_row(row) for row in rows]

    def add_quick_note(self, session_id: int, topic_id: int, text: str) -> int:
        if self.ping_manager and self.is_active:
            self.ping_manager.reset_idle()

        now = now_local_iso()

        return db.execute(
            "INSERT INTO quick_notes (session_id, topic_id, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, topic_id, text, now)
        )

    def get_quick_notes(self, session_id: int):
        rows = db.fetchall(
            "SELECT * FROM quick_notes WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,)
        )
        return [QuickNote.from_row(row) for row in rows]

    def get_sessions_by_topic(self, topic_id: int):
        rows = db.fetchall(
            "SELECT * FROM sessions WHERE topic_id = ? ORDER BY start_time DESC",
            (topic_id,)
        )
        return [Session.from_row(row) for row in rows]

    def get_all_sessions(self):
        rows = db.fetchall("SELECT * FROM sessions ORDER BY start_time DESC")
        return [Session.from_row(row) for row in rows]

    def delete_session(self, session_id: int):
        db.execute("DELETE FROM session_state_logs WHERE session_id = ?", (session_id,))
        db.execute("DELETE FROM quick_notes WHERE session_id = ?", (session_id,))
        db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))