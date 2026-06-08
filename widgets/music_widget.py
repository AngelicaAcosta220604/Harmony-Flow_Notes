# Компактный плеер
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QSlider
)
from PySide6.QtCore import Qt


class MusicWidget(QWidget):
    """
    Прототип виджета управления музыкой для фокус-сессии.
    Поддерживает:
    - выбор звука
    - play / pause
    - громкость
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # ---------------------------------------------------------
        # Заголовок
        # ---------------------------------------------------------
        self.title = QLabel("Музыка")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.title)

        # ---------------------------------------------------------
        # Выбор звука
        # ---------------------------------------------------------
        sound_row = QHBoxLayout()

        self.sound_label = QLabel("Звук:")
        sound_row.addWidget(self.sound_label)

        self.sound_select = QComboBox()
        # позже: self.sound_select.addItems(sounds_manager.list_sounds())
        self.sound_select.addItems(["rain", "forest", "cafe", "white_noise"])
        sound_row.addWidget(self.sound_select)

        self.layout.addLayout(sound_row)

        # ---------------------------------------------------------
        # Кнопки Play / Pause
        # ---------------------------------------------------------
        btn_row = QHBoxLayout()

        self.btn_play = QPushButton("▶")
        self.btn_pause = QPushButton("⏸")

        btn_row.addWidget(self.btn_play)
        btn_row.addWidget(self.btn_pause)

        self.layout.addLayout(btn_row)

        # ---------------------------------------------------------
        # Громкость
        # ---------------------------------------------------------
        vol_row = QHBoxLayout()

        self.vol_label = QLabel("Громкость:")
        vol_row.addWidget(self.vol_label)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        vol_row.addWidget(self.volume_slider)

        self.layout.addLayout(vol_row)

    # ---------------------------------------------------------
    # Методы для интеграции с MusicController
    # ---------------------------------------------------------

    def get_selected_sound(self) -> str:
        return self.sound_select.currentText()

    def set_volume(self, value: int):
        self.volume_slider.setValue(value)

    def get_volume(self) -> float:
        return self.volume_slider.value() / 100
