# widgets/state_sliders.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider
)
from PySide6.QtCore import Qt, QTimer
import time


class StateSliders(QWidget):
    """
    Блок трёх плавных ползунков состояния:
    - Концентрация
    - Энергия
    - Интерес
    Значения: 0–100
    У каждого ползунка свой таймер автосохранения
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Для каждого ползунка храним время последнего сохранения
        self.last_save_time = {
            "concentration": 0,
            "energy": 0,
            "interest": 0
        }

        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(12)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Концентрация
        self.concentration_row = self._create_slider_row("🧠 Концентрация", "concentration")
        self.layout.addLayout(self.concentration_row["layout"])

        # Энергия
        self.energy_row = self._create_slider_row("⚡ Энергия", "energy")
        self.layout.addLayout(self.energy_row["layout"])

        # Интерес
        self.interest_row = self._create_slider_row("❤️ Интерес", "interest")
        self.layout.addLayout(self.interest_row["layout"])

    def _create_slider_row(self, title: str, metric: str):
        """Создаёт строку с ползунком (название сверху)"""
        row = {}

        # Вертикальный layout для строки
        layout = QVBoxLayout()
        layout.setSpacing(6)

        # Название (сверху, слева)
        label = QLabel(title)
        label.setStyleSheet("font-size: 12px; color: #555;")
        layout.addWidget(label)

        # Ползунок
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(50)
        slider.setStyleSheet("""
            QSlider {
                height: 24px;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #E0E0E0;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #FF9800;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                background: #FF9800;
                border-radius: 8px;
                margin: -5px 0;
            }
            QSlider::handle:hover {
                background: #F57C00;
            }
        """)
        layout.addWidget(slider)

        row["layout"] = layout
        row["slider"] = slider
        row["label"] = label
        row["metric"] = metric
        row["debounce_timer"] = QTimer()
        row["debounce_timer"].setSingleShot(True)

        return row

    # =========================================================
    # ПОЛУЧЕНИЕ ЗНАЧЕНИЙ
    # =========================================================

    def get_concentration(self) -> int:
        return self.concentration_row["slider"].value()

    def get_energy(self) -> int:
        return self.energy_row["slider"].value()

    def get_interest(self) -> int:
        return self.interest_row["slider"].value()

    def get_all_values(self) -> dict:
        return {
            "concentration": self.get_concentration(),
            "energy": self.get_energy(),
            "interest": self.get_interest()
        }

    # =========================================================
    # УСТАНОВКА ЗНАЧЕНИЙ
    # =========================================================

    def set_concentration(self, value: int):
        self.concentration_row["slider"].setValue(value)

    def set_energy(self, value: int):
        self.energy_row["slider"].setValue(value)

    def set_interest(self, value: int):
        self.interest_row["slider"].setValue(value)

    def set_all(self, concentration: int, energy: int, interest: int):
        self.set_concentration(concentration)
        self.set_energy(energy)
        self.set_interest(interest)

    # =========================================================
    # ПОДКЛЮЧЕНИЕ КОЛБЭКА С СОХРАНЕНИЕМ
    # =========================================================

    def connect_save_callback(self, callback):
        """
        Подключает функцию сохранения для каждого ползунка отдельно.
        callback будет вызван с параметрами (metric, value, minute)
        """
        self.save_callback = callback

        # Подключаем каждый ползунок с отдельным таймером
        self._connect_slider(self.concentration_row)
        self._connect_slider(self.energy_row)
        self._connect_slider(self.interest_row)

    def _connect_slider(self, row):
        """Подключает один ползунок с отдельным debounce"""
        metric = row["metric"]
        timer = row["debounce_timer"]
        slider = row["slider"]

        def on_value_changed(value):
            # Останавливаем старый таймер
            timer.stop()
            # Запоминаем текущее значение
            timer.setProperty("pending_value", value)
            # Запускаем новый таймер
            timer.timeout.connect(lambda: self._do_save(metric, value))
            timer.start(500)  # 500 мс задержка

        slider.valueChanged.connect(on_value_changed)

    def _do_save(self, metric: str, value: int):
        """Сохраняет значение, если с прошлого сохранения прошло 5 минут"""
        now = time.time()

        if now - self.last_save_time[metric] >= 300:  # 5 минут = 300 секунд
            self.last_save_time[metric] = now
            if hasattr(self, 'save_callback'):
                self.save_callback(metric, value)