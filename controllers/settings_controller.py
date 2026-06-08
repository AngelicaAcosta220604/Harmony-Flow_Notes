# controllers/settings_controller.py
"""
SettingsController — контроллер для работы с настройками приложения.

Реализует:
- получение настройки по ключу
- установка значения
- удаление настройки
- получение всех настроек
- безопасное хранение параметров приложения

Используется в settings_view.py, music_controller.py и других модулях.
"""

from database.db_manager import db
from models.settings import Setting


class SettingsController:

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ЗНАЧЕНИЯ ПО КЛЮЧУ
    # ---------------------------------------------------------
    def get(self, key: str) -> str | None:
        """
        Возвращает значение настройки по ключу.
        Если ключа нет — возвращает None.
        """
        row = db.fetchone("SELECT * FROM settings WHERE key = ?", (key,))
        return row["value"] if row else None

    # ---------------------------------------------------------
    # УСТАНОВКА ЗНАЧЕНИЯ
    # ---------------------------------------------------------
    def set(self, key: str, value: str):
        """
        Устанавливает значение настройки.
        Если ключ существует — обновляет.
        Если нет — создаёт новую запись.
        """
        exists = db.fetchone("SELECT key FROM settings WHERE key = ?", (key,))

        if exists:
            db.execute("UPDATE settings SET value = ? WHERE key = ?", (value, key))
        else:
            db.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))

    # ---------------------------------------------------------
    # УДАЛЕНИЕ НАСТРОЙКИ
    # ---------------------------------------------------------
    def delete(self, key: str):
        """
        Удаляет настройку по ключу.
        """
        db.execute("DELETE FROM settings WHERE key = ?", (key,))

    # ---------------------------------------------------------
    # ПОЛУЧЕНИЕ ВСЕХ НАСТРОЕК
    # ---------------------------------------------------------
    def get_all(self) -> list[Setting]:
        """
        Возвращает список всех настроек.
        """
        rows = db.fetchall("SELECT * FROM settings ORDER BY key ASC")
        return [Setting.from_row(row) for row in rows]

    # ---------------------------------------------------------
    # УСТАНОВКА ЗНАЧЕНИЯ ПО УМОЛЧАНИЮ
    # ---------------------------------------------------------
    def set_default(self, key: str, default_value: str):
        """
        Устанавливает значение по умолчанию, если ключ отсутствует.
        """
        if self.get(key) is None:
            self.set(key, default_value)
# Чтение/запись настроек