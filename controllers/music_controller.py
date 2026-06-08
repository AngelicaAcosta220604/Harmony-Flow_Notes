from PySide6.QtCore import QObject, QTimer, Signal, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

from utils.sound_manager import SoundsManager
from controllers.settings_controller import SettingsController


class MusicController(QObject):
    """
    MusicController — улучшенный контроллер фоновой музыки.
    Полностью совместим с PySide6 Qt6 (без QMediaContent).
    """

    # Сигналы для UI
    started = Signal(str)       # звук начал играть
    stopped = Signal()          # звук остановлен
    changed = Signal(str)       # звук переключён
    volumeChanged = Signal(float)

    def __init__(self):
        super().__init__()

        self.settings = SettingsController()
        self.sounds = SoundsManager()

        # Аудио
        self.audio = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio)

        # Состояние
        self.current_sound = None
        self.is_playing = False

        # Fade
        self.fade_timer = QTimer()
        self.fade_timer.timeout.connect(self._fade_step)
        self.fade_target = None
        self.fade_speed = 0.05

        # Автоповтор
        self.player.mediaStatusChanged.connect(self._on_media_status)

        # Устанавливаем громкость из настроек
        volume = float(self.settings.get("volume") or 0.5)
        self.audio.setVolume(volume)

    # ---------------------------------------------------------
    # ВОСПРОИЗВЕДЕНИЕ
    # ---------------------------------------------------------
    def play(self, sound_name: str):
        """
        Воспроизводит звук с fade-in.
        """
        path = self.sounds.get_path(sound_name)
        if not path:
            print(f"[MusicController] Файл не найден: {sound_name}")
            return

        self.current_sound = sound_name
        self.player.setSource(QUrl.fromLocalFile(str(path)))

        # Начинаем с нулевой громкости
        self.audio.setVolume(0.0)
        self.player.play()
        self.is_playing = True

        self.started.emit(sound_name)

        # Запускаем fade-in
        self.fade_target = float(self.settings.get("volume") or 0.5)
        self.fade_speed = 0.03
        self.fade_timer.start(30)

    # ---------------------------------------------------------
    # ОСТАНОВКА
    # ---------------------------------------------------------
    def stop(self):
        """
        Останавливает звук с fade-out.
        """
        if not self.is_playing:
            return

        self.fade_target = 0.0
        self.fade_speed = -0.03
        self.fade_timer.start(30)

    def _fade_step(self):
        """
        Плавное изменение громкости.
        """
        current = self.audio.volume()
        new = current + self.fade_speed

        # Достигли цели
        if (self.fade_speed > 0 and new >= self.fade_target) or \
           (self.fade_speed < 0 and new <= self.fade_target):

            self.audio.setVolume(self.fade_target)
            self.fade_timer.stop()

            # Если это fade-out — останавливаем
            if self.fade_target == 0.0:
                self.player.stop()
                self.is_playing = False
                self.stopped.emit()

            return

        self.audio.setVolume(new)

    # ---------------------------------------------------------
    # ПЕРЕКЛЮЧЕНИЕ ЗВУКА
    # ---------------------------------------------------------
    def switch(self, sound_name: str):
        """
        Плавно переключает звук.
        """
        if sound_name == self.current_sound:
            return

        # Сначала fade-out
        self.fade_target = 0.0
        self.fade_speed = -0.03
        self.fade_timer.start(30)

        # После fade-out — запускаем новый звук
        def start_new():
            self.fade_timer.timeout.disconnect(start_new)
            self.play(sound_name)
            self.changed.emit(sound_name)

        self.fade_timer.timeout.connect(start_new)

    # ---------------------------------------------------------
    # АВТОПОВТОР
    # ---------------------------------------------------------
    def _on_media_status(self, status):
        """
        Автоматически перезапускает звук, если он закончился.
        """
        if status == QMediaPlayer.EndOfMedia and self.is_playing:
            self.player.play()

    # ---------------------------------------------------------
    # ГРОМКОСТЬ
    # ---------------------------------------------------------
    def set_volume(self, value: float):
        """
        Плавно меняет громкость.
        """
        self.settings.set("volume", str(value))
        self.audio.setVolume(value)
        self.volumeChanged.emit(value)

    def get_volume(self) -> float:
        return self.audio.volume()

    # ---------------------------------------------------------
    # СТАТУС
    # ---------------------------------------------------------
    def is_active(self) -> bool:
        return self.is_playing
