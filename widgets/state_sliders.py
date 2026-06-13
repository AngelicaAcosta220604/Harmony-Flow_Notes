# widgets/state_sliders.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider
)
from PySide6.QtCore import Qt, QTimer
import time


class StateSliders(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.last_save_time = {
            "concentration": 0,
            "energy": 0,
            "interest": 0
        }

        self.save_interval_seconds = 300  # 5 минут

        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(12)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.concentration_row = self._create_slider_row("🧠 Концентрация", "concentration")
        self.layout.addLayout(self.concentration_row["layout"])

        self.energy_row = self._create_slider_row("⚡ Энергия", "energy")
        self.layout.addLayout(self.energy_row["layout"])

        self.interest_row = self._create_slider_row("❤️ Интерес", "interest")
        self.layout.addLayout(self.interest_row["layout"])

    def _create_slider_row(self, title: str, metric: str):
        row = {}

        layout = QVBoxLayout()
        layout.setSpacing(6)

        label = QLabel(title)
        label.setStyleSheet("font-size: 12px; color: #555;")
        layout.addWidget(label)

        slider_container = QHBoxLayout()
        slider_container.setSpacing(10)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(50)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(10)
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
        slider_container.addWidget(slider)

        value_label = QLabel("50")
        value_label.setFixedWidth(35)
        value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        value_label.setStyleSheet("font-size: 11px; color: #888; font-weight: bold;")
        slider_container.addWidget(value_label)

        layout.addLayout(slider_container)

        row["layout"] = layout
        row["slider"] = slider
        row["value_label"] = value_label
        row["label"] = label
        row["metric"] = metric
        row["debounce_timer"] = QTimer()
        row["debounce_timer"].setSingleShot(True)

        slider.valueChanged.connect(lambda v, lbl=value_label: lbl.setText(str(v)))

        return row

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

    def connect_save_callback(self, callback):
        self.save_callback = callback
        self._connect_slider(self.concentration_row)
        self._connect_slider(self.energy_row)
        self._connect_slider(self.interest_row)

    def _connect_slider(self, row):
        metric = row["metric"]
        timer = row["debounce_timer"]
        slider = row["slider"]

        def on_value_changed(value):
            timer.stop()
            try:
                timer.timeout.disconnect()
            except:
                pass
            timer.timeout.connect(lambda: self._do_save(metric, value))
            timer.start(500)

        slider.valueChanged.connect(on_value_changed)

    def _do_save(self, metric: str, value: int):
        now = time.time()

        if now - self.last_save_time[metric] >= self.save_interval_seconds:
            self.last_save_time[metric] = now
            if hasattr(self, 'save_callback'):
                self.save_callback(metric, value)