# controllers/session_state_log_controller.py
"""
SessionStateLogController — контроллер для логов состояния во время фокус-сессии.

Реализует:
- добавление логов (concentration / energy / interest / pause / resume)
- получение логов по сессии
- удаление логов
- получение логов по типу
- получение минутных данных для графиков

Используется в session_controller и analytics_controller.
"""

from database.db_manager import db
from models.session_state_log import SessionStateLog
from utils.local_time import now_local_iso


class SessionStateLogController:

    # ---------------------------------------------------------
    # ДОБАВЛЕНИЕ ЛОГА
    # ---------------------------------------------------------
    def add_log(self, session_id: int, metric: str, value: int, minute: int | None = None):
        """
        Добавляет лог состояния.
        metric:
            - concentration
            - energy
            - interest
            - pause
            - resume
        value: 0–100 (кроме pause/resume)
        minute: номер минуты сессии
        """
        now = now_local_iso()
        query = """
            INSERT INTO session_state_logs (session_id, metric, value, created_at, minute)
            VALUES (?, ?, ?, ?, ?)
        """
        db.execute(query, (session_id, metric, value, now, minute))

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ВСЕХ ЛОГОВ СЕССИИ
    # ---------------------------------------------------------
    def get_logs(self, session_id: int) -> list[SessionStateLog]:
        """Возвращает все логи сессии."""
        rows = db.fetchall(
            "SELECT * FROM session_state_logs WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        )
        return [SessionStateLog.from_row(row) for row in rows]

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ЛОГОВ ПО ТИПУ
    # ---------------------------------------------------------
    def get_logs_by_metric(self, session_id: int, metric: str) -> list[SessionStateLog]:
        """Возвращает логи сессии по указанной метрике."""
        rows = db.fetchall(
            """
            SELECT * FROM session_state_logs
            WHERE session_id = ? AND metric = ?
            ORDER BY minute ASC
            """,
            (session_id, metric)
        )
        return [SessionStateLog.from_row(row) for row in rows]

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ДАННЫХ ДЛЯ ГРАФИКОВ
    # ---------------------------------------------------------
    def get_graph_data(self, session_id: int) -> dict:
        """
        Возвращает:
        {
            "minutes": [...],
            "concentration": [...],
            "energy": [...],
            "interest": [...]
        }
        """
        logs = self.get_logs(session_id)

        minutes = []
        concentration = []
        energy = []
        interest = []

        for log in logs:
            if log.metric == "concentration":
                minutes.append(log.minute)
                concentration.append(log.value)
            elif log.metric == "energy":
                energy.append(log.value)
            elif log.metric == "interest":
                interest.append(log.value)

        return {
            "minutes": minutes,
            "concentration": concentration,
            "energy": energy,
            "interest": interest
        }

    # ---------------------------------------------------------
    # УДАЛЕНИЕ ЛОГОВ СЕССИИ
    # ---------------------------------------------------------
    def delete_logs(self, session_id: int):
        """Удаляет все логи, связанные с сессией."""
        db.execute("DELETE FROM session_state_logs WHERE session_id = ?", (session_id,))