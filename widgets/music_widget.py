# widgets/music_widget.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QMenu
)
from PySide6.QtCore import Qt, QTimer, QPoint, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


class MusicWidget(QWidget):
    """Полноценный музыкальный плеер для фокус-сессии"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Настройки
        self.current_sound_key = "off"
        self.current_sound_name = "Отключено"
        self.is_playing = False
        self.current_volume = 70
        self.play_mode = "loop"

        # Звуки: ключ -> (отображаемое имя, файл)
        self.sounds = {
            "off": ("🔇 Отключено", None),
            "rain": ("🌧 Дождь", "rain.mp3"),
            "forest": ("🌲 Лес", "forest.mp3"),
            "cafe": ("☕ Кафе", "cafe.mp3"),
            "white_noise": ("⚪ Белый шум", "white_noise.mp3"),
        }

        # Медиа-объекты
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(self.current_volume / 100)

        # Подключаем сигнал окончания трека
        self.player.mediaStatusChanged.connect(self._on_media_status)

        # Путь к папке со звуками
        from pathlib import Path
        self.sounds_dir = Path(__file__).resolve().parents[1] / "resources" / "sounds"

        self.setup_ui()
        self.setup_volume_popup()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)

        # Полоска прогресса
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setValue(0)
        self.progress_slider.setStyleSheet("""
            QSlider {
                height: 4px;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #E0E0E0;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #FF9800;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                width: 10px;
                height: 10px;
                background: #FF9800;
                border-radius: 5px;
                margin: -3px 0;
            }
        """)
        self.progress_slider.sliderMoved.connect(self._seek)
        main_layout.addWidget(self.progress_slider)

        # Основная строка управления
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)

        # Кнопка предыдущий
        self.prev_btn = QPushButton("⏮")
        self.prev_btn.setFixedSize(28, 28)
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover { color: #FF9800; }
        """)
        controls_layout.addWidget(self.prev_btn)

        # Кнопка пауза/плей
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(32, 32)
        self.play_btn.setCursor(Qt.PointingHandCursor)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #2C3E50;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover { color: #FF9800; }
        """)
        self.play_btn.clicked.connect(self._toggle_play)
        controls_layout.addWidget(self.play_btn)

        # Кнопка следующий
        self.next_btn = QPushButton("⏭")
        self.next_btn.setFixedSize(28, 28)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover { color: #FF9800; }
        """)
        controls_layout.addWidget(self.next_btn)

        # Контейнер для названия
        self.sound_container = QWidget()
        self.sound_container.setFixedWidth(120)
        sound_layout = QHBoxLayout(self.sound_container)
        sound_layout.setContentsMargins(0, 0, 0, 0)

        self.sound_name_label = QLabel("🔇 Отключено")
        self.sound_name_label.setCursor(Qt.PointingHandCursor)
        self.sound_name_label.setStyleSheet("""
            QLabel {
                color: #2C3E50;
                font-size: 11px;
                background-color: #F5F5F5;
                border-radius: 12px;
                padding: 4px 8px;
            }
        """)
        self.sound_name_label.mousePressEvent = self._show_sound_menu
        sound_layout.addWidget(self.sound_name_label)

        controls_layout.addWidget(self.sound_container)
        controls_layout.addStretch()

        # Кнопка режима
        self.mode_btn = QPushButton("🔁")
        self.mode_btn.setFixedSize(28, 28)
        self.mode_btn.setCursor(Qt.PointingHandCursor)
        self.mode_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover { color: #FF9800; }
        """)
        self.mode_btn.clicked.connect(self._toggle_play_mode)
        controls_layout.addWidget(self.mode_btn)

        # Кнопка громкости
        self.volume_btn = QPushButton("🔊")
        self.volume_btn.setFixedSize(28, 28)
        self.volume_btn.setCursor(Qt.PointingHandCursor)
        self.volume_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover { color: #FF9800; }
        """)
        self.volume_btn.clicked.connect(self._toggle_mute)
        controls_layout.addWidget(self.volume_btn)

        main_layout.addLayout(controls_layout)

        # Таймер для обновления прогресса
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._update_progress)
        self.progress_timer.start(500)

    def setup_volume_popup(self):
        """Вертикальный ползунок громкости"""
        self.volume_popup = QWidget(None)
        self.volume_popup.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.volume_popup.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #DDD;
                border-radius: 15px;
            }
        """)

        volume_layout = QVBoxLayout(self.volume_popup)
        volume_layout.setContentsMargins(12, 12, 12, 12)
        volume_layout.setSpacing(8)

        self.volume_slider = QSlider(Qt.Vertical)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.current_volume)
        self.volume_slider.setFixedHeight(80)
        self.volume_slider.setFixedWidth(24)
        self.volume_slider.setStyleSheet("""
            QSlider {
                width: 4px;
            }
            QSlider::groove:vertical {
                width: 4px;
                background: #E0E0E0;
                border-radius: 2px;
            }
            QSlider::sub-page:vertical {
                background: #FF9800;
                border-radius: 2px;
            }
            QSlider::handle:vertical {
                width: 12px;
                height: 12px;
                background: #FF9800;
                border-radius: 6px;
                margin: -4px -4px;
            }
        """)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        volume_layout.addWidget(self.volume_slider, alignment=Qt.AlignCenter)

        self.volume_label = QLabel(f"{self.current_volume}%")
        self.volume_label.setAlignment(Qt.AlignCenter)
        self.volume_label.setStyleSheet("color: #666; font-size: 10px;")
        volume_layout.addWidget(self.volume_label)

        self.volume_timer = QTimer()
        self.volume_timer.setSingleShot(True)
        self.volume_timer.timeout.connect(self.volume_popup.hide)

        self.volume_btn.installEventFilter(self)
        self.volume_slider.installEventFilter(self)

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        if obj == self.volume_btn and event.type() == QEvent.Enter:
            btn_pos = self.volume_btn.mapToGlobal(QPoint(0, -95))
            self.volume_popup.move(btn_pos)
            self.volume_popup.show()
            self.volume_timer.stop()
        elif obj == self.volume_btn and event.type() == QEvent.Leave:
            self.volume_timer.start(500)
        elif obj == self.volume_slider and event.type() == QEvent.Enter:
            self.volume_timer.stop()
        elif obj == self.volume_slider and event.type() == QEvent.Leave:
            self.volume_timer.start(500)
        return super().eventFilter(obj, event)

    def _play_sound(self, sound_key: str):
        """Воспроизводит выбранный звук"""
        if sound_key == "off" or sound_key not in self.sounds:
            self._stop()
            return

        sound_file = self.sounds[sound_key][1]
        if not sound_file:
            return

        file_path = self.sounds_dir / sound_file
        if not file_path.exists():
            print(f"[MusicWidget] Файл не найден: {file_path}")
            return

        self.player.setSource(QUrl.fromLocalFile(str(file_path)))
        self.player.play()
        self.is_playing = True
        self.play_btn.setText("⏸")

    def _stop(self):
        """Останавливает воспроизведение"""
        self.player.stop()
        self.is_playing = False
        self.play_btn.setText("▶")
        self.progress_slider.setValue(0)

    def _toggle_play(self):
        """Play / Пауза"""
        if self.current_sound_key == "off":
            return

        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.play_btn.setText("▶")
            self.is_playing = False
        else:
            self.player.play()
            self.play_btn.setText("⏸")
            self.is_playing = True

    def _seek(self, position: int):
        """Перемотка"""
        if self.player.duration() > 0:
            self.player.setPosition(int(position * self.player.duration() / 100))

    def _update_progress(self):
        """Обновляет ползунок прогресса"""
        if self.player.duration() > 0 and self.player.position() > 0:
            progress = int(self.player.position() * 100 / self.player.duration())
            self.progress_slider.setValue(progress)

    def _on_media_status(self, status):
        """Обработка окончания трека"""
        if status == QMediaPlayer.EndOfMedia:
            if self.play_mode == "repeat_one":
                self.player.setPosition(0)
                self.player.play()
            elif self.play_mode == "loop":
                self.player.setPosition(0)
                self.player.play()
            else:
                self.is_playing = False
                self.play_btn.setText("▶")

    def _show_sound_menu(self, event):
        """Меню выбора звука"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #DDD;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: #FFF3E0;
            }
        """)

        for key, (name, _) in self.sounds.items():
            action = menu.addAction(name)
            action.triggered.connect(lambda checked, k=key: self._set_sound(k))

        menu.exec(self.sound_name_label.mapToGlobal(event.pos()))

    def _set_sound(self, sound_key: str):
        """Устанавливает выбранный звук"""
        self.current_sound_key = sound_key
        self.current_sound_name = self.sounds[sound_key][0]
        self.sound_name_label.setText(self.current_sound_name)

        if sound_key == "off":
            self._stop()
        else:
            self._play_sound(sound_key)

    def _toggle_mute(self):
        """Вкл/Выкл звука"""
        if self.current_volume > 0:
            self.current_volume = 0
            self.volume_slider.setValue(0)
            self.volume_label.setText("0%")
            self.volume_btn.setText("🔇")
            self.audio_output.setVolume(0)
        else:
            self.current_volume = 70
            self.volume_slider.setValue(70)
            self.volume_label.setText("70%")
            self.volume_btn.setText("🔊")
            self.audio_output.setVolume(0.7)

    def _on_volume_changed(self, value: int):
        self.current_volume = value
        self.volume_label.setText(f"{value}%")
        self.volume_btn.setText("🔇" if value == 0 else "🔊")
        self.audio_output.setVolume(value / 100)

    def _toggle_play_mode(self):
        modes = [("🔁", "loop"), ("🔂", "repeat_one"), ("🔀", "shuffle")]
        current_index = next((i for i, (icon, mode) in enumerate(modes) if mode == self.play_mode), 0)
        next_index = (current_index + 1) % len(modes)
        self.play_mode = modes[next_index][1]
        self.mode_btn.setText(modes[next_index][0])

        mode_names = {"loop": "Повтор списка", "repeat_one": "Повтор одной", "shuffle": "Случайный"}
        self.mode_btn.setToolTip(mode_names[self.play_mode])

    def get_selected_sound(self) -> str:
        return self.current_sound_key

    def set_volume(self, value: int):
        self.current_volume = value
        self.volume_slider.setValue(value)
        self.audio_output.setVolume(value / 100)

    def get_volume(self) -> int:
        return self.current_volume

    def set_playing_state(self, is_playing: bool):
        self.play_btn.setText("⏸" if is_playing else "▶")