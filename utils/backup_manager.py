# managers/backup_manager.py
"""
BackupManager — менеджер резервного копирования базы данных.

Реализует:
- создание резервной копии SQLite
- хранение бэкапов в папке backups/
- автоматическое именование с датой и временем
- удаление старых бэкапов (опционально)

Используется в настройках или вручную через UI.
"""

from pathlib import Path
from datetime import datetime
import shutil


class BackupManager:

    def __init__(self, db_path: str = "database/app.db"):
        self.db_path = Path(db_path)
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)

    # ---------------------------------------------------------
    # СОЗДАНИЕ БЭКАПА
    # ---------------------------------------------------------
    def create_backup(self) -> Path:
        """
        Создаёт резервную копию базы данных.
        Возвращает путь к созданному файлу.
        """
        if not self.db_path.exists():
            raise FileNotFoundError("Файл базы данных не найден")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = self.backup_dir / f"backup_{timestamp}.db"

        shutil.copy2(self.db_path, backup_file)
        return backup_file

    # ---------------------------------------------------------
    # УДАЛЕНИЕ СТАРЫХ БЭКАПОВ
    # ---------------------------------------------------------
    def delete_old_backups(self, keep_last: int = 5):
        """
        Удаляет старые бэкапы, оставляя только N последних.
        """
        backups = sorted(self.backup_dir.glob("backup_*.db"))

        if len(backups) <= keep_last:
            return

        for old in backups[:-keep_last]:
            old.unlink()
