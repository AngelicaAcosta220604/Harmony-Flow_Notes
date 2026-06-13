# widgets/ping_manager.py

from PySide6.QtCore import QTimer, QObject, Signal


class PingManager(QObject):
    """
    Менеджер контроля активности пользователя.
    """

    pingNeeded = Signal()
    timeoutReached = Signal()

    def __init__(self, idle_minutes: int = 15, timeout_seconds: int = 30, parent=None):
        super().__init__(parent)
        self.idle_minutes = idle_minutes
        self.timeout_seconds = timeout_seconds

        self.idle_timer = QTimer()
        self.idle_timer.setSingleShot(True)
        self.idle_timer.timeout.connect(self._on_idle)

        self.response_timer = QTimer()
        self.response_timer.setSingleShot(True)
        self.response_timer.timeout.connect(self._on_timeout)

        self.reset_idle()

    def reset_idle(self):
        """Сбрасывает таймер бездействия"""
        self.idle_timer.start(self.idle_minutes * 60 * 1000)
        if self.response_timer.isActive():
            self.response_timer.stop()

    def _on_idle(self):
        """Пользователь бездействует"""
        self.pingNeeded.emit()
        self.response_timer.start(self.timeout_seconds * 1000)

    def _on_timeout(self):
        """Пользователь не ответил на пинг"""
        self.timeoutReached.emit()

    def user_confirmed(self):
        """Пользователь подтвердил активность"""
        self.reset_idle()

    def stop(self):
        """Останавливает все таймеры"""
        self.idle_timer.stop()
        self.response_timer.stop()