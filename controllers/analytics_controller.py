# controllers/analytics_controller.py

from database.db_manager import db
from models.session import Session
from models.task import Task
from models.session_state_log import SessionStateLog
from datetime import datetime
from typing import List, Optional, Tuple


class AnalyticsController:
    """Базовый контроллер для аналитики (не привязан к теме)"""

    def __init__(self):
        pass

    # ==================== ПОЛУЧЕНИЕ ДАННЫХ ====================

    def get_all_sessions(self) -> List[Session]:
        rows = db.fetchall("SELECT * FROM sessions ORDER BY start_time DESC")
        return [Session.from_row(row) for row in rows]

    def get_all_tasks(self) -> List[Task]:
        rows = db.fetchall("SELECT * FROM tasks")
        return [Task.from_row(row) for row in rows]

    def get_sessions_in_range(self, start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> List[Session]:
        """Возвращает сессии за указанный период"""
        sessions = self.get_all_sessions()
        if not start_date and not end_date:
            return sessions

        filtered = []
        for session in sessions:
            if not session.start_time:
                continue
            start = datetime.fromisoformat(session.start_time)
            if start_date and start < start_date:
                continue
            if end_date and start > end_date:
                continue
            filtered.append(session)
        return filtered

    def get_tasks_in_range(self, start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[Task]:
        """Возвращает задачи за указанный период"""
        tasks = self.get_all_tasks()
        if not start_date and not end_date:
            return tasks

        filtered = []
        for task in tasks:
            if not task.created_at:
                continue
            created = datetime.fromisoformat(task.created_at)
            if start_date and created < start_date:
                continue
            if end_date and created > end_date:
                continue
            filtered.append(task)
        return filtered

    def get_session_logs(self, session_id: int) -> List[SessionStateLog]:
        rows = db.fetchall(
            "SELECT * FROM session_state_logs WHERE session_id = ? ORDER BY minute ASC",
            (session_id,)
        )
        return [SessionStateLog.from_row(row) for row in rows]

    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================

    def _avg_metric(self, sessions: List[Session], metric: str) -> float:
        """Вычисляет среднее значение метрики для списка сессий"""
        values = []
        for session in sessions:
            logs = self.get_session_logs(session.id)
            for log in logs:
                if log.metric == metric:
                    values.append(log.value)
        return sum(values) / len(values) if values else 0

    def _get_metric_timeline(self, session: Session, metric: str) -> Tuple[List[int], List[int]]:
        """Возвращает (минуты, значения) для графика"""
        logs = self.get_session_logs(session.id)
        minutes = []
        values = []
        for log in logs:
            if log.metric == metric:
                minutes.append(log.minute or 0)
                values.append(log.value)
        return minutes, values

    def _get_peaks(self, session: Session, metric: str) -> Tuple[int, int]:
        """Возвращает (максимальное значение, минимальное значение)"""
        logs = self.get_session_logs(session.id)
        values = [log.value for log in logs if log.metric == metric]
        if not values:
            return (0, 0)
        return (max(values), min(values))

    # ==================== СТАТИСТИКА ПО СЕССИЯМ ====================

    def get_session_stats(self, sessions: List[Session]) -> dict:
        """Общая статистика по списку сессий"""
        if not sessions:
            return self._empty_stats()

        total_sessions = len(sessions)
        total_minutes = sum(s.duration_minutes or 0 for s in sessions)
        avg_duration = total_minutes / total_sessions if total_sessions else 0

        # Средние показатели
        avg_concentration = self._avg_metric(sessions, 'concentration')
        avg_energy = self._avg_metric(sessions, 'energy')
        avg_interest = self._avg_metric(sessions, 'interest')

        # Первая и последняя сессия
        dates = [datetime.fromisoformat(s.start_time) for s in sessions if s.start_time]
        first_session = min(dates).strftime("%d.%m.%Y") if dates else "—"
        last_session = max(dates).strftime("%d.%m.%Y") if dates else "—"

        return {
            "total_sessions": total_sessions,
            "total_minutes": total_minutes,
            "total_hours": round(total_minutes / 60, 1),
            "avg_duration": round(avg_duration, 1),
            "avg_concentration": round(avg_concentration, 2),
            "avg_energy": round(avg_energy, 2),
            "avg_interest": round(avg_interest, 2),
            "first_session": first_session,
            "last_session": last_session
        }

    def get_time_of_day_stats(self, sessions: List[Session]) -> dict:
        """Аналитика по часам суток"""
        hour_stats = {}
        for h in range(24):
            hour_stats[h] = {"count": 0, "concentration": [], "energy": [], "interest": []}

        for session in sessions:
            if not session.start_time:
                continue
            hour = datetime.fromisoformat(session.start_time).hour

            hour_stats[hour]["count"] += 1

            logs = self.get_session_logs(session.id)
            for log in logs:
                if log.metric == "concentration":
                    hour_stats[hour]["concentration"].append(log.value)
                elif log.metric == "energy":
                    hour_stats[hour]["energy"].append(log.value)
                elif log.metric == "interest":
                    hour_stats[hour]["interest"].append(log.value)

        # Вычисляем средние
        for h in range(24):
            if hour_stats[h]["concentration"]:
                hour_stats[h]["avg_concentration"] = sum(hour_stats[h]["concentration"]) / len(hour_stats[h]["concentration"])
            if hour_stats[h]["energy"]:
                hour_stats[h]["avg_energy"] = sum(hour_stats[h]["energy"]) / len(hour_stats[h]["energy"])
            if hour_stats[h]["interest"]:
                hour_stats[h]["avg_interest"] = sum(hour_stats[h]["interest"]) / len(hour_stats[h]["interest"])

        return hour_stats

    def get_day_of_week_stats(self, sessions: List[Session]) -> dict:
        """Аналитика по дням недели"""
        day_stats = {i: {"count": 0, "concentration": [], "energy": [], "interest": []} for i in range(7)}
        days_ru = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]

        for session in sessions:
            if not session.start_time:
                continue
            dow = datetime.fromisoformat(session.start_time).weekday()

            day_stats[dow]["count"] += 1

            logs = self.get_session_logs(session.id)
            for log in logs:
                if log.metric == "concentration":
                    day_stats[dow]["concentration"].append(log.value)
                elif log.metric == "energy":
                    day_stats[dow]["energy"].append(log.value)
                elif log.metric == "interest":
                    day_stats[dow]["interest"].append(log.value)

        for d in range(7):
            if day_stats[d]["concentration"]:
                day_stats[d]["avg_concentration"] = sum(day_stats[d]["concentration"]) / len(day_stats[d]["concentration"])
            if day_stats[d]["energy"]:
                day_stats[d]["avg_energy"] = sum(day_stats[d]["energy"]) / len(day_stats[d]["energy"])
            if day_stats[d]["interest"]:
                day_stats[d]["avg_interest"] = sum(day_stats[d]["interest"]) / len(day_stats[d]["interest"])
            day_stats[d]["name"] = days_ru[d]

        return day_stats

    def get_session_timeline(self, sessions: List[Session], metric: str) -> Tuple[List[str], List[float]]:
        """Возвращает динамику метрики по сессиям (для графика прогресса)"""
        dates = []
        values = []
        for session in sessions:
            if not session.start_time:
                continue
            dates.append(datetime.fromisoformat(session.start_time).strftime("%d.%m"))
            logs = self.get_session_logs(session.id)
            metric_values = [log.value for log in logs if log.metric == metric]
            if metric_values:
                values.append(sum(metric_values) / len(metric_values))
            else:
                values.append(0.0)
        return dates, values

    # ==================== СТАТИСТИКА ПО ЗАДАЧАМ ====================

    def get_task_stats(self, tasks: List[Task]) -> dict:
        """Статистика по задачам"""
        if not tasks:
            return {"total": 0, "completed": 0, "overdue": 0, "completion_rate": 0}

        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == "completed")
        overdue = sum(1 for t in tasks if t.status == "overdue" or (t.deadline and datetime.fromisoformat(t.deadline) < datetime.now()))

        return {
            "total": total,
            "completed": completed,
            "overdue": overdue,
            "completion_rate": round(completed / total * 100, 1) if total else 0
        }

    # ==================== ТЕКСТОВЫЕ ВЫВОДЫ ====================

    def generate_insights(self, sessions: List[Session]) -> List[str]:
        """Генерирует текстовые выводы на основе сессий"""
        insights = []

        if not sessions:
            return ["Нет данных для анализа. Проведите несколько сессий."]

        stats = self.get_session_stats(sessions)

        # Общая информация
        insights.append(
            f"📊 Всего проведено {stats['total_sessions']} сессий, общей длительностью {stats['total_hours']} часов.")

        # Средние показатели
        if stats['avg_concentration'] >= 4:
            insights.append(f"🧠 Отличная концентрация! Средний показатель {stats['avg_concentration']}/5.")
        elif stats['avg_concentration'] >= 3:
            insights.append(f"🧠 Хорошая концентрация: {stats['avg_concentration']}/5. Есть потенциал для роста.")
        else:
            insights.append(
                f"🧠 Концентрация ниже среднего ({stats['avg_concentration']}/5). Попробуйте использовать метод Помодоро.")

        if stats['avg_energy'] >= 4:
            insights.append(f"⚡ Энергия на высоте! Средний показатель {stats['avg_energy']}/5.")
        elif stats['avg_energy'] <= 2:
            insights.append(
                f"⚡ Уровень энергии низкий ({stats['avg_energy']}/5). Возможно, стоит заниматься в другое время суток.")

        # Анализ по времени суток
        hour_stats = self.get_time_of_day_stats(sessions)
        best_hour = max(range(24),
                        key=lambda h: hour_stats[h].get("avg_concentration", 0) if hour_stats[h]["count"] > 0 else 0)
        best_hour_count = hour_stats[best_hour]["count"]
        best_hour_conc = hour_stats[best_hour].get("avg_concentration", 0)

        if best_hour_count > 0 and best_hour_conc > 0:
            insights.append(
                f"⏰ Лучшее время для занятий: {best_hour:02d}:00. Концентрация в это время достигает {best_hour_conc:.1f}/5.")

        # Анализ по дням недели
        day_stats = self.get_day_of_week_stats(sessions)
        best_day = max(range(7), key=lambda d: day_stats[d].get("avg_concentration", 0) if day_stats[d]["count"] > 0 else 0)
        best_day_conc = day_stats[best_day].get("avg_concentration", 0)

        if best_day_conc > 0:
            insights.append(f"📆 Самый продуктивный день: {day_stats[best_day]['name']} (концентрация {best_day_conc:.1f}/5).")

        # Динамика (если сессий больше 3)
        if len(sessions) >= 3:
            dates, conc_values = self.get_session_timeline(sessions, "concentration")
            if len(conc_values) >= 3:
                trend = conc_values[-1] - conc_values[0]
                if trend > 0.5:
                    insights.append(
                        f"📈 Отличный прогресс! Концентрация выросла с {conc_values[0]:.1f} до {conc_values[-1]:.1f} за последние сессии.")
                elif trend < -0.5:
                    insights.append(
                        f"📉 Концентрация снижается. Возможно, стоит отдохнуть или пересмотреть подход к занятиям.")

        # Рекомендация по длительности
        if stats['avg_duration'] > 90:
            insights.append(
                f"💡 Сессии длиннее 90 минут могут снижать эффективность. Рекомендуемая длительность: 45-60 минут.")
        elif stats['avg_duration'] < 30 and stats['total_sessions'] > 3:
            insights.append(
                f"💡 Сессии короткие ({stats['avg_duration']} мин). Попробуйте увеличить длительность до 45-60 минут.")

        return insights

    def generate_session_insight(self, session: Session) -> List[str]:
        """Генерирует выводы по конкретной сессии"""
        insights = []

        if not session:
            return ["Сессия не найдена"]

        logs = self.get_session_logs(session.id)
        if not logs:
            return ["Нет данных о состоянии во время этой сессии"]

        # Получаем значения
        conc_vals = [log.value for log in logs if log.metric == "concentration"]
        energy_vals = [log.value for log in logs if log.metric == "energy"]
        interest_vals = [log.value for log in logs if log.metric == "interest"]

        avg_conc = sum(conc_vals) / len(conc_vals) if conc_vals else 0
        avg_energy = sum(energy_vals) / len(energy_vals) if energy_vals else 0
        avg_interest = sum(interest_vals) / len(interest_vals) if interest_vals else 0
        max_conc = max(conc_vals) if conc_vals else 0
        max_energy = max(energy_vals) if energy_vals else 0
        max_interest = max(interest_vals) if interest_vals else 0

        # Находим минуту падения концентрации
        drop_minute = None
        if len(conc_vals) >= 2:
            for i in range(1, len(conc_vals)):
                if conc_vals[i] < conc_vals[i - 1] - 1:
                    drop_minute = logs[i].minute
                    break

        insights.append(f"📊 Длительность сессии: {session.duration_minutes or '?'} минут")
        insights.append(f"🎯 Пиковая концентрация: {max_conc}/5, средняя: {avg_conc:.1f}/5")
        insights.append(f"⚡ Пик энергии: {max_energy}/5, средняя: {avg_energy:.1f}/5")
        insights.append(f"❤️ Пик интереса: {max_interest}/5, средний: {avg_interest:.1f}/5")

        if avg_conc >= 4 and avg_interest >= 4:
            insights.append("✨ Вы были в состоянии ПОТОКА! Отличная сессия!")
        elif avg_conc <= 2 or avg_energy <= 2:
            insights.append("😴 Сессия была тяжёлой. Возможно, стоит отдохнуть перед следующим занятием.")

        if drop_minute:
            insights.append(f"⚠️ Концентрация заметно упала на {drop_minute} минуте. Хороший момент для перерыва.")

        return insights

    def _empty_stats(self) -> dict:
        return {
            "total_sessions": 0,
            "total_minutes": 0,
            "total_hours": 0,
            "avg_duration": 0,
            "avg_concentration": 0,
            "avg_energy": 0,
            "avg_interest": 0,
            "first_session": "—",
            "last_session": "—"
        }