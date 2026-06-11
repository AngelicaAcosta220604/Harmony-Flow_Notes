# controllers/topic_analytics_controller.py

from controllers.analytics_controller import AnalyticsController
from database.db_manager import db
from models.session import Session
from models.task import Task


class TopicAnalyticsController(AnalyticsController):
    """Контроллер для аналитики по конкретной теме (наследует базовый)"""

    def __init__(self, topic_id: int):
        super().__init__()
        self.topic_id = topic_id

    def get_topic_sessions(self) -> list:
        """Возвращает сессии только по текущей теме"""
        rows = db.fetchall(
            "SELECT * FROM sessions WHERE topic_id = ? ORDER BY start_time DESC",
            (self.topic_id,)
        )
        return [Session.from_row(row) for row in rows]

    def get_topic_tasks(self) -> list:
        """Возвращает задачи только по текущей теме"""
        rows = db.fetchall(
            "SELECT * FROM tasks WHERE topic_id = ?",
            (self.topic_id,)
        )
        return [Task.from_row(row) for row in rows]

    def get_topic_stats(self) -> dict:
        """Статистика по теме (использует родительские методы с отфильтрованными данными)"""
        sessions = self.get_topic_sessions()
        return self.get_session_stats(sessions)

    def get_topic_insights(self) -> list:
        """Выводы по теме"""
        sessions = self.get_topic_sessions()
        return self.generate_insights(sessions)

    def get_session_analytics(self, session_id: int) -> dict:
        """Детальная аналитика по конкретной сессии"""
        session = next((s for s in self.get_topic_sessions() if s.id == session_id), None)
        if not session:
            return {"error": "Сессия не найдена"}

        logs = self.get_session_logs(session_id)

        # Данные для графиков
        graph_data = self.get_graph_data(session_id)

        # Пиковые значения
        conc_vals = [log.value for log in logs if log.metric == "concentration"]
        energy_vals = [log.value for log in logs if log.metric == "energy"]
        interest_vals = [log.value for log in logs if log.metric == "interest"]

        return {
            "session": session,
            "graph_data": graph_data,
            "peaks": {
                "concentration": max(conc_vals) if conc_vals else 0,
                "energy": max(energy_vals) if energy_vals else 0,
                "interest": max(interest_vals) if interest_vals else 0
            },
            "averages": {
                "concentration": sum(conc_vals) / len(conc_vals) if conc_vals else 0,
                "energy": sum(energy_vals) / len(energy_vals) if energy_vals else 0,
                "interest": sum(interest_vals) / len(interest_vals) if interest_vals else 0
            },
            "insights": self.generate_session_insight(session)
        }

    def get_graph_data(self, session_id: int) -> dict:
        """Возвращает данные для графиков по минутам"""
        logs = self.get_session_logs(session_id)
        minutes = []
        concentration = []
        energy = []
        interest = []

        for log in logs:
            if log.metric == "concentration":
                minutes.append(log.minute or 0)
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