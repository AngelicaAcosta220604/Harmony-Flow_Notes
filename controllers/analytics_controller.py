# controllers/analytics_controller.py
"""
AnalyticsController — контроллер для аналитики и статистики.

Реализует:
- статистику по времени (день/неделя/месяц)
- анализ фокус-сессий
- средние значения концентрации/энергии/интереса
- данные для графиков
- статистику по темам

Используется в analytics_view.py.
"""

from database.db_manager import db
from models.session import Session
from models.session_state_log import SessionStateLog
from datetime import datetime, timedelta
from collections import defaultdict


class AnalyticsController:

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ВСЕХ СЕССИЙ
    # ---------------------------------------------------------
    def get_all_sessions(self) -> list[Session]:
        rows = db.fetchall("SELECT * FROM sessions ORDER BY start_time DESC")
        return [Session.from_row(row) for row in rows]

    # ---------------------------------------------------------
    # СТАТИСТИКА ПО ВРЕМЕНИ (день/неделя/месяц)
    # ---------------------------------------------------------
    def get_time_stats(self):
        """
        Возвращает:
        - total_today
        - total_week
        - total_month
        В минутах.
        """
        now = datetime.now()

        rows = db.fetchall("SELECT * FROM sessions")
        total_today = 0
        total_week = 0
        total_month = 0

        for row in rows:
            session = Session.from_row(row)
            if not session.duration:
                continue

            start = datetime.fromisoformat(session.start_time)

            if start.date() == now.date():
                total_today += session.duration

            if now - timedelta(days=7) <= start:
                total_week += session.duration

            if start.month == now.month and start.year == now.year:
                total_month += session.duration

        return {
            "today": total_today,
            "week": total_week,
            "month": total_month
        }

    # ---------------------------------------------------------
    # DAILY STATS (для теста test_daily_stats)
    # ---------------------------------------------------------
    def get_daily_stats(self, day: datetime):
        """
        Статистика за конкретный день:
        - total_sessions
        - total_minutes
        - avg_focus
        """
        rows = db.fetchall("SELECT * FROM sessions")

        total_sessions = 0
        total_minutes = 0
        focus_values = []

        for row in rows:
            session = Session.from_row(row)
            if not session.duration:
                continue

            start = datetime.fromisoformat(session.start_time)
            if start.date() != day.date():
                continue

            total_sessions += 1
            total_minutes += session.duration
            if session.focus is not None:
                focus_values.append(session.focus)

        avg_focus = sum(focus_values) / len(focus_values) if focus_values else 0

        return {
            "total_sessions": total_sessions,
            "total_minutes": total_minutes,
            "avg_focus": avg_focus
        }

    # ---------------------------------------------------------
    # WEEKLY STATS (для теста test_weekly_stats)
    # ---------------------------------------------------------
    def get_weekly_stats(self, now: datetime):
        """
        Статистика за последние 7 дней:
        - total_sessions
        - total_minutes
        """
        rows = db.fetchall("SELECT * FROM sessions")

        total_sessions = 0
        total_minutes = 0

        week_start = now - timedelta(days=7)

        for row in rows:
            session = Session.from_row(row)
            if not session.duration:
                continue

            start = datetime.fromisoformat(session.start_time)
            if start < week_start:
                continue

            total_sessions += 1
            total_minutes += session.duration

        return {
            "total_sessions": total_sessions,
            "total_minutes": total_minutes
        }

    # ---------------------------------------------------------
    # ЛОГИ СЕССИИ
    # ---------------------------------------------------------
    def get_session_logs(self, session_id: int) -> list[SessionStateLog]:
        rows = db.fetchall(
            "SELECT * FROM session_state_logs WHERE session_id = ? ORDER BY minute ASC",
            (session_id,)
        )
        return [SessionStateLog.from_row(row) for row in rows]

    # ---------------------------------------------------------
    # СРЕДНИЕ ЗНАЧЕНИЯ СОСТОЯНИЙ
    # ---------------------------------------------------------
    def get_average_states(self, session_id: int):
        """
        Возвращает средние значения:
        - concentration
        - energy
        - interest
        """
        logs = self.get_session_logs(session_id)

        metrics = defaultdict(list)

        for log in logs:
            if log.metric in ("concentration", "energy", "interest"):
                metrics[log.metric].append(log.value)

        def avg(values):
            return sum(values) / len(values) if values else 0

        return {
            "concentration": avg(metrics["concentration"]),
            "energy": avg(metrics["energy"]),
            "interest": avg(metrics["interest"])
        }

    # ---------------------------------------------------------
    # ДАННЫЕ ДЛЯ ГРАФИКОВ (минутные)
    # ---------------------------------------------------------
    def get_graph_data(self, session_id: int):
        """
        Возвращает данные для графиков:
        - список минут
        - концентрация
        - энергия
        - интерес
        """
        logs = self.get_session_logs(session_id)

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
    # СТАТИСТИКА ПО ТЕМАМ (адаптирована под test_topic_stats)
    # ---------------------------------------------------------
    def get_topic_stats(self):
        """
        Возвращает словарь:
        {
            topic_id: {
                "minutes": total_minutes
            }
        }
        """
        rows = db.fetchall("SELECT topic_id, duration FROM sessions")

        stats = defaultdict(int)

        for row in rows:
            if row["duration"]:
                stats[row["topic_id"]] += row["duration"]

        # адаптация под тест: stats[1]["minutes"] == 20
        return {tid: {"minutes": minutes} for tid, minutes in stats.items()}

    # ---------------------------------------------------------
    # ОБЩАЯ СТАТИСТИКА ДЛЯ DASHBOARD
    # ---------------------------------------------------------
    def get_dashboard_summary(self):
        """
        Возвращает:
        - общее время
        - количество сессий
        - средняя длительность
        """
        rows = db.fetchall("SELECT * FROM sessions")

        total_time = 0
        count = 0

        for row in rows:
            session = Session.from_row(row)
            if session.duration:
                total_time += session.duration
                count += 1

        avg_duration = total_time / count if count else 0

        return {
            "total_time": total_time,
            "sessions": count,
            "avg_duration": avg_duration
        }
