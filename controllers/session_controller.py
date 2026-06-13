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
        self.session_resume_time = None  # Время последнего возобновления (для подсчёта отрезка)
        print("[DEBUG SessionController] Инициализация")

    def set_ping_manager(self, ping_manager):
        self.ping_manager = ping_manager
        if self.ping_manager:
            self.ping_manager.pingNeeded.connect(self._on_ping_needed)
            self.ping_manager.timeoutReached.connect(self._on_ping_timeout)

    def stop_ping_manager(self):
        """Останавливает пинг-менеджер"""
        if self.ping_manager:
            self.ping_manager.stop()

    def _on_ping_needed(self):
        if self.is_active and self.current_session_id:
            self.ping_needed.emit()

    def _on_ping_timeout(self):
        if self.is_active and self.current_session_id:
            self.auto_pause_session()

    def auto_pause_session(self):
        if self.current_session_id:
            print(f"[DEBUG] auto_pause_session: сессия {self.current_session_id}")
            self.pause_session(self.current_session_id, auto=True)

    def user_responded_to_ping(self):
        if self.ping_manager:
            self.ping_manager.user_confirmed()

    def _print_total_active(self, session_id: int):
        row = db.fetchone("SELECT total_active_seconds FROM sessions WHERE id = ?", (session_id,))
        if row:
            print(f"[DEBUG] total_active_seconds = {row['total_active_seconds']}")

    def start_session(self, topic_id: int) -> int:
        print(f"[DEBUG] start_session: topic_id={topic_id}")

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
        self.session_resume_time = datetime.now()  # Запоминаем время возобновления

        if self.ping_manager:
            self.ping_manager.reset_idle()

        self._update_topic_timestamp(topic_id)
        return self.current_session_id

    def get_session(self, session_id: int):
        row = db.fetchone("SELECT * FROM sessions WHERE id = ?", (session_id,))
        return Session.from_row(row) if row else None

    def pause_session(self, session_id: int, auto: bool = False):
        print(f"[DEBUG] pause_session: сессия {session_id}, auto={auto}")

        # Получаем сессию из БД для проверки реального статуса
        session_from_db = self.get_session(session_id)
        if not session_from_db:
            print(f"[DEBUG] pause: сессия {session_id} не найдена")
            return

        # Проверяем, активна ли сессия В ПАМЯТИ (только если есть активный таймер)
        # НЕ проверяем статус в БД, потому что при перезапуске статус может быть 'active',
        # но в памяти сессия не активна!
        is_session_active_in_memory = self.is_active and self.current_session_id == session_id

        print(f"[DEBUG] is_active (memory)={self.is_active}, session_resume_time={self.session_resume_time}")

        # Добавляем время ТОЛЬКО если сессия активна в памяти (есть запущенный таймер)
        if is_session_active_in_memory and self.session_resume_time:
            elapsed = int((datetime.now() - self.session_resume_time).total_seconds())
            if elapsed > 0:
                print(f"[DEBUG] pause: прошло {elapsed} сек, добавляем к total_active_seconds")

                db.execute(
                    "UPDATE sessions SET total_active_seconds = total_active_seconds + ? WHERE id = ?",
                    (elapsed, session_id)
                )
                self._print_total_active(session_id)
            else:
                print(f"[DEBUG] pause: elapsed=0, время не добавлено")
        else:
            print(f"[DEBUG] pause: условие не выполнено, время НЕ добавлено")
            if not is_session_active_in_memory:
                print(f"[DEBUG]   причина: сессия не активна в памяти (self.is_active={self.is_active})")
            elif not self.session_resume_time:
                print(f"[DEBUG]   причина: нет session_resume_time")

        # Сбрасываем время возобновления
        self.session_resume_time = None

        # Обновляем статус в БД
        new_status = 'auto_paused' if auto else 'paused'
        db.execute(
            "UPDATE sessions SET status = ? WHERE id = ?",
            (new_status, session_id)
        )

        # Обновляем состояние в памяти
        self.is_active = False

        if auto:
            self.session_auto_paused.emit(session_id)

    def resume_session(self, session_id: int):
        print(f"[DEBUG] resume_session: сессия {session_id}")

        session = self.get_session(session_id)
        if not session:
            return

        # Обновляем статус на active
        db.execute(
            "UPDATE sessions SET status = ? WHERE id = ?",
            ('active', session_id)
        )
        self.is_active = True
        self.current_session_id = session_id
        self.session_resume_time = datetime.now()  # Запоминаем время возобновления
        print(f"[DEBUG] resume: session_resume_time={self.session_resume_time}")

    def end_session(self, session_id: int, duration: int = None):
        print(f"[DEBUG] end_session: сессия {session_id}")

        session = self.get_session(session_id)
        topic_id = session.topic_id if session else None
        if not session:
            print(f"[DEBUG] end_session: сессия {session_id} не найдена!")
            return

        end_time = now_local_iso()

        # Добавляем последний активный отрезок, если сессия активна
        if self.is_active and self.session_resume_time and self.current_session_id == session_id:
            elapsed = int((datetime.now() - self.session_resume_time).total_seconds())
            if elapsed > 0:
                print(f"[DEBUG] end: последний отрезок = {elapsed} сек")
                db.execute(
                    "UPDATE sessions SET total_active_seconds = total_active_seconds + ? WHERE id = ?",
                    (elapsed, session_id)
                )
            self.session_resume_time = None
            self._print_total_active(session_id)

        # Получаем общее активное время
        updated_session = self.get_session(session_id)
        total_seconds = updated_session.total_active_seconds if updated_session else 0
        duration_minutes = total_seconds // 60
        print(f"[DEBUG] end: итого total_seconds={total_seconds}, duration_minutes={duration_minutes}")

        db.execute(
            """
            UPDATE sessions
            SET end_time = ?, duration_minutes = ?, status = ?
            WHERE id = ?
            """,
            (end_time, duration_minutes, 'completed', session_id)
        )

        if self.current_session_id == session_id:
            self.is_active = False
            self.current_session_id = None
            self.session_resume_time = None

        if self.ping_manager:
            self.ping_manager.idle_timer.stop()
            self.ping_manager.response_timer.stop()

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
        print(f"[DEBUG] delete_session: удаление сессии {session_id}")
        db.execute("DELETE FROM session_state_logs WHERE session_id = ?", (session_id,))
        db.execute("DELETE FROM quick_notes WHERE session_id = ?", (session_id,))
        db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

    def check_and_auto_complete(self, session_id: int, pause_duration_minutes: int = 20):
        """
        Проверяет, не пора ли автоматически завершить сессию из-за долгой паузы.
        Вызывается при загрузке сессии из истории.
        """
        session = self.get_session(session_id)
        if not session or session.status != "paused":
            return False

        try:
            start = datetime.fromisoformat(session.start_time)
            if (datetime.now() - start).total_seconds() > pause_duration_minutes * 60:
                self.end_session(session_id)
                return True
        except:
            pass
        return False

    def has_active_or_paused_session(self, topic_id: int = None) -> tuple:
        """
        Проверяет, есть ли незавершённые сессии.
        Возвращает (has_session, session_id, status, topic_id)
        ВОЗВРАЩАЕТ САМУЮ СВЕЖУЮ сессию (по start_time DESC)
        """
        if topic_id:
            rows = db.fetchall(
                """SELECT id, status, topic_id FROM sessions 
                   WHERE topic_id = ? AND status IN ('active', 'paused', 'auto_paused')
                   ORDER BY start_time DESC""",  # ← Добавлено ORDER BY
                (topic_id,)
            )
        else:
            rows = db.fetchall(
                """SELECT id, status, topic_id FROM sessions 
                   WHERE status IN ('active', 'paused', 'auto_paused')
                   ORDER BY start_time DESC""",  # ← Добавлено ORDER BY
            )

        if rows:
            session = rows[0]  # Берем самую свежую
            return True, session['id'], session['status'], session['topic_id']
        return False, None, None, None

    def check_and_pause_active_session(self):
        """Проверяет и ставит на паузу любую активную сессию (при запуске приложения)"""
        # Получаем ВСЕ активные сессии и ставим их на паузу
        rows = db.fetchall(
            """SELECT id, status, start_time FROM sessions 
               WHERE status = 'active'
               ORDER BY start_time DESC"""
        )
        for row in rows:
            session_id = row['id']
            # Просто меняем статус в БД, так как таймер не активен
            db.execute(
                "UPDATE sessions SET status = ? WHERE id = ?",
                ('paused', session_id)
            )
            print(f"[DEBUG] При запуске: сессия {session_id} переведена в статус 'paused'")

    def save_slider_values(self, session_id: int, concentration: int, energy: int, interest: int):
        """Сохраняет позиции ползунков в БД"""
        db.execute(
            "UPDATE sessions SET concentration = ?, energy = ?, interest = ? WHERE id = ?",
            (concentration, energy, interest, session_id)
        )

    def get_slider_values(self, session_id: int) -> dict:
        """Возвращает сохранённые позиции ползунков"""
        row = db.fetchone(
            "SELECT concentration, energy, interest FROM sessions WHERE id = ?",
            (session_id,)
        )
        if row:
            return {
                "concentration": row.get("concentration", 50),
                "energy": row.get("energy", 50),
                "interest": row.get("interest", 50)
            }
        return {"concentration": 50, "energy": 50, "interest": 50}