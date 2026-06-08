# managers/ping_manager.py
"""
PingManager — менеджер проверки активности пользователя.

Реализует:
- таймер бездействия
- показ уведомления "Вы ещё здесь?"
- callback при отсутствии ответа
- сброс таймера при активности

Используется в главном окне приложения.
"""

from PySide6.QtCore import QTimer, QObject, Signal


class PingManager(QObject):
    """
    Менеджер, который отслеживает активность пользователя.
    Если пользователь долго не взаимодействует с приложением —
    вызывается сигнал pingNeeded.
    """

    pingNeeded = Signal()       # показать уведомление
    timeoutReached = Signal()   # пользователь не ответил

    def __init__(self, idle_ms: int = 5 * 60 * 1000, timeout_ms: int = 20 * 1000):
        """
        idle_ms — время бездействия до показа пинга (по умолчанию 5 минут)
        timeout_ms — время ожидания ответа (по умолчанию 20 секунд)
        """
        super().__init__()

        self.idle_ms = idle_ms
        self.timeout_ms = timeout_ms

        # Таймер бездействия
        self.idle_timer = QTimer()
        self.idle_timer.setSingleShot(True)
        self.idle_timer.timeout.connect(self._on_idle)

        # Таймер ожидания ответа
        self.timeout_timer = QTimer()
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(self._on_timeout)

        self.reset_idle()

    # ---------------------------------------------------------
    # СБРОС ТАЙМЕРА БЕЗДЕЙСТВИЯ
    # ---------------------------------------------------------
    def reset_idle(self):
        """
        Сбрасывает таймер бездействия.
        Вызывается при любом действии пользователя:
        - движение мыши
        - клик
        - ввод текста
        """
        self.idle_timer.start(self.idle_ms)

        # Если пинг был показан — отменяем ожидание ответа
        if self.timeout_timer.isActive():
            self.timeout_timer.stop()

    # ---------------------------------------------------------
    # ПОЛЬЗОВАТЕЛЬ БЕЗДЕЙСТВУЕТ
    # ---------------------------------------------------------
    def _on_idle(self):
        """
        Пользователь не активен — показываем пинг.
        """
        self.pingNeeded.emit()
        self.timeout_timer.start(self.timeout_ms)

    # ---------------------------------------------------------
    # ПОЛЬЗОВАТЕЛЬ НЕ ОТВЕТИЛ НА ПИНГ
    # ---------------------------------------------------------
    def _on_timeout(self):
        """
        Пользователь не ответил на пинг — вызываем callback.
        Например: ставим сессию на паузу.
        """
        self.timeoutReached.emit()

    # ---------------------------------------------------------
    # ПОЛЬЗОВАТЕЛЬ ОТВЕТИЛ НА ПИНГ
    # ---------------------------------------------------------
    def user_confirmed(self):
        """
        Вызывается, когда пользователь нажал "Да, я здесь".
        """
        self.timeout_timer.stop()
        self.reset_idle()
