# Переключение светлой/тёмной темы
# utils/theme_manager.py
"""
ThemeManager — менеджер тем оформления приложения.

Реализует:
- хранение светлой и тёмной темы
- применение темы к приложению
- загрузку QSS-стилей
- централизованное управление цветами
- интеграцию с SettingsController

Используется в главном окне и настройках.
"""

from pathlib import Path
from PySide6.QtWidgets import QApplication
from controllers.settings_controller import SettingsController


class ThemeManager:

    def __init__(self):
        self.settings = SettingsController()

        # Папка со стилями
        self.styles_dir = Path(__file__).resolve().parents[1] / "resources" / "styles"

        # Список доступных тем
        self.themes = {
            "light": self.styles_dir / "light.qss",
            "dark": self.styles_dir / "dark.qss",
        }

    # ---------------------------------------------------------
    # ПРИМЕНИТЬ ТЕМУ
    # ---------------------------------------------------------
    def apply_theme(self, theme_name: str):
        """
        Применяет тему к приложению.
        """
        if theme_name not in self.themes:
            raise ValueError(f"Тема '{theme_name}' не найдена")

        qss_path = self.themes[theme_name]

        if not qss_path.exists():
            raise FileNotFoundError(f"Файл темы не найден: {qss_path}")

        qss = qss_path.read_text(encoding="utf-8")
        QApplication.instance().setStyleSheet(qss)

        # Сохраняем выбор
        self.settings.set("theme", theme_name)

    # ---------------------------------------------------------
    # ЗАГРУЗИТЬ ТЕМУ ИЗ НАСТРОЕК
    # ---------------------------------------------------------
    def load_saved_theme(self):
        """
        Загружает тему, сохранённую в настройках.
        Если нет — применяет светлую.
        """
        theme = self.settings.get("theme") or "light"
        self.apply_theme(theme)

    # ---------------------------------------------------------
    # СПИСОК ДОСТУПНЫХ ТЕМ
    # ---------------------------------------------------------
    def list_themes(self) -> list[str]:
        """
        Возвращает список доступных тем.
        """
        return list(self.themes.keys())

    # ---------------------------------------------------------
    # РЕГИСТРАЦИЯ НОВОЙ ТЕМЫ
    # ---------------------------------------------------------
    def register_theme(self, name: str, qss_file: str | Path):
        """
        Добавляет новую тему.
        Пример:
            register_theme("blue", "blue.qss")
        """
        path = Path(qss_file)
        if not path.exists():
            raise FileNotFoundError("Файл QSS не найден")

        self.themes[name] = path
