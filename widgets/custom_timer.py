# Виджет таймера (ЧЧ:ММ:СС)
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import QTimer, Qt


class CustomTimer(QWidget):
    """
    Таймер для фокус-сессии.
    Поддерживает:
    - старт с нуля
    - старт с заданного времени
    - паузу
    - продолжение
    - сброс
    - отображение в формате HH:MM:SS
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Время в секундах
        self.seconds = 0
        self.running = False

        # UI
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.label = QLabel("00:00:00")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 48px; font-weight: bold;")
        self.layout.addWidget(self.label)

        # Таймер Qt
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)

    # ---------------------------------------------------------
    # Управление таймером
    # ---------------------------------------------------------

    def start(self, start_seconds: int = 0):
        """
        Запускает таймер.
        Если указано start_seconds — начинает с этого времени.
        """
        self.seconds = start_seconds
        self.running = True
        self.timer.start(1000)
        self._update_label()

    def set_seconds(self, seconds: int):
        """
        Устанавливает время таймера (без запуска).
        """
        self.seconds = seconds
        self._update_label()

    def pause(self):
        """Ставит таймер на паузу."""
        if self.running:
            self.running = False
            self.timer.stop()

    def resume(self):
        """Продолжает таймер после паузы (сохраняя текущее время)."""
        if not self.running:
            self.running = True
            self.timer.start(1000)

    def reset(self):
        """Сбрасывает таймер."""
        self.seconds = 0
        self.running = False
        self.timer.stop()
        self._update_label()

    # ---------------------------------------------------------
    # Внутренние методы
    # ---------------------------------------------------------

    def _tick(self):
        """Каждую секунду увеличивает время."""
        if self.running:
            self.seconds += 1
            self._update_label()

    def _update_label(self):
        """Обновляет текст таймера."""
        h = self.seconds // 3600
        m = (self.seconds % 3600) // 60
        s = self.seconds % 60
        self.label.setText(f"{h:02d}:{m:02d}:{s:02d}")

    # ---------------------------------------------------------
    # Получение времени
    # ---------------------------------------------------------

    def get_seconds(self) -> int:
        return self.seconds