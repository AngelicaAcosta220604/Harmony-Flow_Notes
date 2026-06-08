# database/db_manager.py
"""
DatabaseManager — центральный класс для работы с SQLite.
Он отвечает за:
- подключение к базе данных
- выполнение запросов
- возврат результатов
- инициализацию таблиц
- управление транзакциями

Это фундамент всего приложения.
"""

import sqlite3
from pathlib import Path


class DatabaseManager:
    """
    Класс-обёртка над sqlite3, обеспечивающий удобный доступ к базе данных.
    Используется всеми контроллерами.
    """

    def __init__(self, db_name: str = "hflow.db"):
        """
        Подключение к базе данных.
        Если файла нет — SQLite создаст его автоматически.

        row_factory позволяет получать строки в виде словарей:
        row["column_name"] вместо row[0]
        """
        # Путь к файлу базы данных
        self.db_path = Path(__file__).resolve().parent / db_name

        # Попытка подключения
        try:
            self.conn = sqlite3.connect(self.db_path)
        except sqlite3.DatabaseError:
            # Если файл не является SQLite — удаляем
            self.db_path.unlink(missing_ok=True)
            # Создаём новый
            self.conn = sqlite3.connect(self.db_path)

        # Настройка формата строк
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        # Включаем foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON;")

        # ⚠ ВАЖНО: сразу инициализируем БД по INIT_QUERIES
        self.init_db()

    # ----------------------------------------------------------------------
    # БАЗОВЫЕ ОПЕРАЦИИ
    # ----------------------------------------------------------------------

    def execute(self, query: str, params: tuple = ()):
        """
        Выполняет запрос, который изменяет данные (INSERT, UPDATE, DELETE).
        Возвращает cursor, чтобы можно было получить lastrowid.
        """
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor

    def fetchone(self, query: str, params: tuple = ()):
        """
        Выполняет SELECT и возвращает одну строку.
        Если данных нет — вернёт None.
        """
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def fetchall(self, query: str, params: tuple = ()):
        """
        Выполняет SELECT и возвращает список строк.
        Каждая строка — sqlite3.Row (словарь).
        """
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    # ----------------------------------------------------------------------
    # ИНИЦИАЛИЗАЦИЯ БАЗЫ
    # ----------------------------------------------------------------------

    def init_db(self):
        """
        Создаёт все таблицы, описанные в db_queries.py.
        Теперь вызывается автоматически в __init__.
        """
        from .db_queries import INIT_QUERIES

        # Если INIT_QUERIES — список строк
        if isinstance(INIT_QUERIES, (list, tuple)):
            for query in INIT_QUERIES:
                self.cursor.execute(query)
        else:
            # Если это одна большая строка со скриптом
            self.cursor.executescript(INIT_QUERIES)

        self.conn.commit()

    # ----------------------------------------------------------------------
    # УТИЛИТЫ
    # ----------------------------------------------------------------------

    def close(self):
        """Закрывает соединение с базой данных."""
        self.conn.close()

    def __del__(self):
        """Гарантированное закрытие соединения при уничтожении объекта."""
        try:
            self.conn.close()
        except:
            pass


# Глобальный экземпляр БД, который используется во всём приложении
db = DatabaseManager()
