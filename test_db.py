from database.db_manager import db
from models.topic import Topic

# 1. Проверка подключения
print("БД создалась?", db.db_path)

# 2. Создадим тему
topic_id = db.execute(
    "INSERT INTO topics (name, type) VALUES (?, ?)",
    ("Тестовая тема", "topic")
)
print(f"Создана тема с id = {topic_id}")

# 3. Прочитаем тему
row = db.fetchone("SELECT * FROM topics WHERE id = ?", (topic_id,))
if row:
    topic = Topic.from_row(row)
    print(f"Прочитали: {topic}")
