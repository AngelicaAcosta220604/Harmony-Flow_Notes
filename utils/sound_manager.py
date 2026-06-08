# Упрощённое управление звуками (QMediaPlayer)
# utils/sounds_manager.py
"""
SoundsManager — менеджер для работы со звуковыми ресурсами.

Реализует:
- хранение списка доступных звуков
- безопасную проверку наличия файлов
- получение пути к звуку
- получение списка звуков для UI
- централизованное управление аудио-ресурсами

Используется в music_controller и settings_view.
"""

from pathlib import Path


class SoundsManager:

    def __init__(self, sounds_dir: str | Path = None):
        """
        sounds_dir — путь к папке со звуками.
        Если не указан — определяется автоматически.
        """
        if sounds_dir is None:
            self.sounds_dir = Path(__file__).resolve().parents[1] / "resources" / "sounds"
        else:
            self.sounds_dir = Path(sounds_dir)

        # Список доступных звуков (ключ → имя файла)
        self.sounds = {
            "rain": "rain.mp3",
            "forest": "forest.mp3",
            "cafe": "cafe.mp3",
            "white_noise": "white_noise.mp3",
        }

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ПУТИ К ЗВУКУ
    # ---------------------------------------------------------
    def get_path(self, sound_name: str) -> Path | None:
        """
        Возвращает путь к звуковому файлу.
        Если звук не найден — None.
        """
        if sound_name not in self.sounds:
            return None

        path = self.sounds_dir / self.sounds[sound_name]
        return path if path.exists() else None

    # ---------------------------------------------------------
    # ПРОВЕРКА НАЛИЧИЯ ВСЕХ ФАЙЛОВ
    # ---------------------------------------------------------
    def validate_sounds(self) -> dict:
        """
        Проверяет наличие всех звуков.
        Возвращает словарь:
        {
            "rain": True,
            "forest": False,
            ...
        }
        """
        result = {}
        for key, filename in self.sounds.items():
            result[key] = (self.sounds_dir / filename).exists()
        return result

    # ---------------------------------------------------------
    # СПИСОК ЗВУКОВ ДЛЯ UI
    # ---------------------------------------------------------
    def list_sounds(self) -> list[str]:
        """
        Возвращает список доступных звуков (ключей).
        """
        return list(self.sounds.keys())

    # ---------------------------------------------------------
    # ДОБАВЛЕНИЕ НОВОГО ЗВУКА
    # ---------------------------------------------------------
    def register_sound(self, key: str, filename: str):
        """
        Регистрирует новый звук.
        Пример:
            register_sound("ocean", "ocean.mp3")
        """
        self.sounds[key] = filename

    # ---------------------------------------------------------
    # УДАЛЕНИЕ ЗВУКА
    # ---------------------------------------------------------
    def unregister_sound(self, key: str):
        """
        Удаляет звук из списка (файл не трогает).
        """
        if key in self.sounds:
            del self.sounds[key]
