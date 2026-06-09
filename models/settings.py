# models/settings.py
class Setting:
    def __init__(self, id: int = None, key: str = "", value: str = ""):
        self.id = id
        self.key = key
        self.value = value

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id=row.get("id"),
            key=row.get("setting_key", ""),
            value=row.get("setting_value", "")
        )