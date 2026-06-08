# controllers/calendar_controller.py
"""
CalendarController — контроллер для календаря.

Реализует:
- получение задач по датам
- задачи на конкретный день
- задачи на неделю / месяц
- группировка задач по дням
- проверка просроченных задач
- генерация календарной сетки для UI

Используется в calendar_view.py.
"""

from database.db_manager import db
from models.task import Task
from datetime import datetime, timedelta, date
import calendar


class CalendarController:

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ВСЕХ ЗАДАЧ С ДЕДЛАЙНОМ
    # ---------------------------------------------------------
    def get_tasks_with_deadlines(self) -> list[Task]:
        """
        Возвращает все задачи, у которых есть дедлайн.
        """
        rows = db.fetchall(
            "SELECT * FROM tasks WHERE deadline IS NOT NULL ORDER BY deadline ASC"
        )
        return [Task.from_row(row) for row in rows]

    # ---------------------------------------------------------
    # ЗАДАЧИ НА КОНКРЕТНЫЙ ДЕНЬ
    # ---------------------------------------------------------
    def get_tasks_for_day(self, target_date: date) -> list[Task]:
        """
        Возвращает задачи, дедлайн которых совпадает с target_date.
        """
        rows = db.fetchall(
            """
            SELECT * FROM tasks
            WHERE DATE(deadline) = DATE(?)
            ORDER BY deadline ASC
            """,
            (target_date,)
        )
        return [Task.from_row(row) for row in rows]

    # ---------------------------------------------------------
    # ЗАДАЧИ НА НЕДЕЛЮ
    # ---------------------------------------------------------
    def get_tasks_for_week(self, start_date: date) -> dict:
        """
        Возвращает словарь:
        {
            date: [tasks]
        }
        """
        result = {}
        for i in range(7):
            day = start_date + timedelta(days=i)
            result[day] = self.get_tasks_for_day(day)
        return result

    # ---------------------------------------------------------
    # ЗАДАЧИ НА МЕСЯЦ
    # ---------------------------------------------------------
    def get_tasks_for_month(self, year: int, month: int) -> dict:
        """
        Возвращает словарь:
        {
            date: [tasks]
        }
        для всех дней месяца.
        """
        _, num_days = calendar.monthrange(year, month)

        result = {}
        for day in range(1, num_days + 1):
            d = date(year, month, day)
            result[d] = self.get_tasks_for_day(d)

        return result

    # ---------------------------------------------------------
    # ГРУППИРОВКА ЗАДАЧ ПО ДНЯМ
    # ---------------------------------------------------------
    def group_tasks_by_day(self) -> dict:
        """
        Возвращает словарь:
        {
            '2025-01-12': [tasks],
            '2025-01-13': [tasks],
            ...
        }
        """
        tasks = self.get_tasks_with_deadlines()
        grouped = {}

        for task in tasks:
            if not task.deadline:
                continue

            day = task.deadline.split(" ")[0]  # YYYY-MM-DD
            grouped.setdefault(day, []).append(task)

        return grouped

    # ---------------------------------------------------------
    # ПРОСРОЧЕННЫЕ ЗАДАЧИ
    # ---------------------------------------------------------
    def get_overdue_tasks(self) -> list[Task]:
        """
        Возвращает список просроченных задач.
        """
        now = datetime.now()

        rows = db.fetchall(
            """
            SELECT * FROM tasks
            WHERE deadline IS NOT NULL AND status = 'active'
            """
        )

        overdue = []
        for row in rows:
            task = Task.from_row(row)
            try:
                deadline_dt = datetime.fromisoformat(task.deadline)
                if deadline_dt < now:
                    overdue.append(task)
            except:
                continue

        return overdue

    # ---------------------------------------------------------
    # КАЛЕНДАРНАЯ СЕТКА ДЛЯ UI
    # ---------------------------------------------------------
    def get_month_grid(self, year: int, month: int) -> list[list[date | None]]:
        """
        Возвращает сетку календаря:
        [
            [date, date, date, date, date, date, date],
            ...
        ].
        где пустые ячейки = None
        """
        cal = calendar.Calendar(firstweekday=0)  # понедельник
        month_days = cal.monthdatescalendar(year, month)

        # Преобразуем в формат:
        # None если день не из текущего месяца
        grid = []
        for week in month_days:
            row = []
            for d in week:
                if d.month == month:
                    row.append(d)
                else:
                    row.append(None)
            grid.append(row)

        return grid
