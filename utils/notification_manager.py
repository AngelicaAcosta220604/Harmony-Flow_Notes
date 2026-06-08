# managers/notification_manager.py
"""
NotificationManager — менеджер напоминаний и уведомлений.

Реализует:
- периодическую проверку задач с дедлайнами
- напоминания о приближающихся дедлайнах
- напоминания по времени (если заданы)
- сигналы для UI: показать уведомление
- безопасную работу с Qt-таймерами

Используется в главном окне приложения.
"""

from PySide6.QtCore import QObject, QTimer, Signal
from datetime import datetime, timedelta
from controllers.task_controller import TaskController
from controllers.settings_controller import SettingsController


class NotificationManager(QObject):
    """
    Менеджер, который каждые N секунд проверяет задачи
    и отправляет сигналы для UI, если нужно показать уведомление.
    """

    notify = Signal(dict)
    # dict содержит:
    # {
    #   "type": "deadline" | "reminder",
    #   "task_id": int,
    #   "title": str,
    #   "message": str
    # }

    def __init__(self, check_interval_ms: int = 60_000):
        """
        check_interval_ms — как часто проверять задачи (по умолчанию 1 минута)
        """
        super().__init__()

        self.tasks = TaskController()
        self.settings = SettingsController()

        # Таймер периодической проверки
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_tasks)
        self.timer.start(check_interval_ms)

        # Кэш отправленных уведомлений, чтобы не спамить
        self.sent_notifications = set()

    # ---------------------------------------------------------
    # ОСНОВНАЯ ПРОВЕРКА
    # ---------------------------------------------------------
    def check_tasks(self):
        """
        Проверяет:
        - просроченные задачи
        - задачи, у которых дедлайн скоро
        - задачи с напоминаниями (если будут добавлены)
        """
        now = datetime.now()

        all_tasks = self.tasks.get_all_tasks()

        for task in all_tasks:
            if not task.deadline:
                continue

            try:
                deadline_dt = datetime.fromisoformat(task.deadline)
            except:
                continue

            # 1) Просроченные задачи
            if deadline_dt < now and task.status == "active":
                self._emit_once(
                    key=f"overdue_{task.id}",
                    payload={
                        "type": "deadline",
                        "task_id": task.id,
                        "title": task.title,
                        "message": "Задача просрочена!"
                    }
                )

            # 2) Приближающийся дедлайн (за 30 минут)
            if now <= deadline_dt <= now + timedelta(minutes=30):
                self._emit_once(
                    key=f"soon_{task.id}",
                    payload={
                        "type": "deadline",
                        "task_id": task.id,
                        "title": task.title,
                        "message": "Дедлайн через 30 минут!"
                    }
                )

            # 3) Напоминания (если будут добавлены в будущем)
            # Здесь можно расширить логику:
            # if task.reminder_time == now ± delta: ...

    # ---------------------------------------------------------
    # ОТПРАВИТЬ УВЕДОМЛЕНИЕ ОДИН РАЗ
    # ---------------------------------------------------------
    def _emit_once(self, key: str, payload: dict):
        """
        Отправляет уведомление только один раз.
        """
        if key in self.sent_notifications:
            return

        self.sent_notifications.add(key)
        self.notify.emit(payload)

    # ---------------------------------------------------------
    # СБРОС УВЕДОМЛЕНИЙ (например, при смене дня)
    # ---------------------------------------------------------
    def reset_notifications(self):
        """
        Полный сброс кэша уведомлений.
        """
        self.sent_notifications.clear()
