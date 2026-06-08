# Ползунки концентрации/энергии/интереса
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider
)
from PySide6.QtCore import Qt


class StateSliders(QWidget):
    """
    Прототип блока трёх ползунков состояния:
    - Концентрация
    - Энергия
    - Интерес

    Значения: 1–5
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # ---------------------------------------------------------
        # Концентрация
        # ---------------------------------------------------------
        self.concentration_row = self._create_slider_row("Концентрация")
        self.layout.addLayout(self.concentration_row["layout"])

        # ---------------------------------------------------------
        # Энергия
        # ---------------------------------------------------------
        self.energy_row = self._create_slider_row("Энергия")
        self.layout.addLayout(self.energy_row["layout"])

        # ---------------------------------------------------------
        # Интерес
        # ---------------------------------------------------------
        self.interest_row = self._create_slider_row("Интерес")
        self.layout.addLayout(self.interest_row["layout"])

    # ---------------------------------------------------------
    # Внутренний метод создания строки слайдера
    # ---------------------------------------------------------
    def _create_slider_row(self, title: str):
        row = {}

        layout = QHBoxLayout()

        label = QLabel(title)
        layout.addWidget(label)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(1, 5)
        slider.setValue(3)
        slider.setTickInterval(1)
        slider.setTickPosition(QSlider.TicksBelow)
        layout.addWidget(slider)

        value_label = QLabel("3")
        layout.addWidget(value_label)

        # обновление значения
        slider.valueChanged.connect(lambda v: value_label.setText(str(v)))

        row["layout"] = layout
        row["slider"] = slider
        row["value_label"] = value_label

        return row

    # ---------------------------------------------------------
    # Методы получения значений
    # ---------------------------------------------------------
    def get_concentration(self) -> int:
        return self.concentration_row["slider"].value()

    def get_energy(self) -> int:
        return self.energy_row["slider"].value()

    def get_interest(self) -> int:
        return self.interest_row["slider"].value()

    # ---------------------------------------------------------
    # Методы установки значений (если нужно)
    # ---------------------------------------------------------
    def set_concentration(self, value: int):
        self.concentration_row["slider"].setValue(value)

    def set_energy(self, value: int):
        self.energy_row["slider"].setValue(value)

    def set_interest(self, value: int):
        self.interest_row["slider"].setValue(value)
