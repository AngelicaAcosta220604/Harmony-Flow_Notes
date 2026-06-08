import sqlite3
import pytest
from database.db_manager import db
from database.db_queries import INIT_QUERIES


@pytest.fixture
def db():
    # создаём временную БД в памяти
    manager = db(":memory:")
    manager.execute_script(INIT_QUERIES)
    return manager


def test_tables_exist(db):
    tables = db.fetchall("""
        SELECT name FROM sqlite_master WHERE type='table';
    """)

    table_names = {t["name"] for t in tables}

    assert "topics" in table_names
    assert "notes" in table_names
    assert "tasks" in table_names
    assert "flashcards" in table_names
    assert "sessions" in table_names
    assert "session_state_logs" in table_names


def test_insert_topic(db):
    db.execute("INSERT INTO topics (name) VALUES (?)", ("Математика",))
    topic = db.fetchone("SELECT * FROM topics WHERE name=?", ("Математика",))

    assert topic is not None
    assert topic["name"] == "Математика"


def test_insert_note_and_relation(db):
    # создаём тему
    db.execute("INSERT INTO topics (name) VALUES (?)", ("Физика",))
    topic = db.fetchone("SELECT * FROM topics WHERE name=?", ("Физика",))

    # создаём заметку
    db.execute(
        "INSERT INTO notes (topic_id, title, content) VALUES (?, ?, ?)",
        (topic["id"], "Заметка", "Текст")
    )

    note = db.fetchone("SELECT * FROM notes WHERE title=?", ("Заметка",))

    assert note is not None
    assert note["topic_id"] == topic["id"]


def test_foreign_key_cascade(db):
    # создаём тему
    db.execute("INSERT INTO topics (name) VALUES (?)", ("Химия",))
    topic = db.fetchone("SELECT * FROM topics WHERE name=?", ("Химия",))

    # создаём заметку
    db.execute(
        "INSERT INTO notes (topic_id, title, content) VALUES (?, ?, ?)",
        (topic["id"], "Нота", "Контент")
    )

    # удаляем тему
    db.execute("DELETE FROM topics WHERE id=?", (topic["id"],))

    # заметка должна удалиться каскадно
    note = db.fetchone("SELECT * FROM notes WHERE title=?", ("Нота",))
    assert note is None
