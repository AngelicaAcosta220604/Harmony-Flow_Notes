# models/settings.py
"""
Модель настройки приложения.
Хранит пары ключ-значение.
"""

class Setting:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    @classmethod
    def from_row(cls, row):
        return cls(
            key=row["key"],
            value=row["value"]
        )
