# controllers/search_controller.py
"""
SearchController — контроллер для глобального поиска по приложению.

Реализует:
- поиск по заметкам
- поиск по задачам
- поиск по карточкам
- поиск по темам
- объединённый поиск search_all()
- ранжирование результатов
- подсветка совпадений (заглушка для UI)

Поиск работает по нескольким таблицам и возвращает структурированные результаты.
"""

from database.db_manager import db


class SearchController:

    # ---------------------------------------------------------
    # ПОИСК ПО ТЕМАМ
    # ---------------------------------------------------------
    def search_topics(self, query: str) -> list[dict]:
        rows = db.fetchall(
            "SELECT id, name FROM topics WHERE name LIKE ?",
            (f"%{query}%",)
        )
        return [
            {
                "type": "topic",
                "id": row["id"],
                "title": row["name"],
                "snippet": None
            }
            for row in rows
        ]

    # ---------------------------------------------------------
    # ПОИСК ПО ЗАМЕТКАМ
    # ---------------------------------------------------------
    def search_notes(self, query: str) -> list[dict]:
        rows = db.fetchall(
            """
            SELECT id, title, content
            FROM notes
            WHERE title LIKE ? OR content LIKE ?
            """,
            (f"%{query}%", f"%{query}%")
        )

        results = []
        for row in rows:
            snippet = self._make_snippet(row["content"], query)
            results.append({
                "type": "note",
                "id": row["id"],
                "title": row["title"],
                "snippet": snippet
            })
        return results

    # ---------------------------------------------------------
    # ПОИСК ПО ЗАДАЧАМ
    # ---------------------------------------------------------
    def search_tasks(self, query: str) -> list[dict]:
        rows = db.fetchall(
            """
            SELECT id, title, description
            FROM tasks
            WHERE title LIKE ? OR description LIKE ?
            """,
            (f"%{query}%", f"%{query}%")
        )

        results = []
        for row in rows:
            snippet = self._make_snippet(row["description"], query)
            results.append({
                "type": "task",
                "id": row["id"],
                "title": row["title"],
                "snippet": snippet
            })
        return results

    # ---------------------------------------------------------
    # ПОИСК ПО КАРТОЧКАМ
    # ---------------------------------------------------------
    def search_flashcards(self, query: str) -> list[dict]:
        rows = db.fetchall(
            """
            SELECT id, question, answer
            FROM flashcards
            WHERE question LIKE ? OR answer LIKE ?
            """,
            (f"%{query}%", f"%{query}%")
        )

        results = []
        for row in rows:
            text = row["question"] or row["answer"]
            snippet = self._make_snippet(text, query)
            results.append({
                "type": "flashcard",
                "id": row["id"],
                "title": row["question"] or "(карточка)",
                "snippet": snippet
            })
        return results

    # ---------------------------------------------------------
    # ГЛОБАЛЬНЫЙ ПОИСК
    # ---------------------------------------------------------
    def search_all(self, query: str) -> list[dict]:
        """
        Выполняет поиск по всем сущностям и возвращает объединённый список.
        """
        if not query.strip():
            return []

        results = []
        results.extend(self.search_topics(query))
        results.extend(self.search_notes(query))
        results.extend(self.search_tasks(query))
        results.extend(self.search_flashcards(query))

        # Ранжирование: сначала точные совпадения, потом частичные
        results.sort(key=lambda r: self._rank(r, query), reverse=True)

        return results

    # ---------------------------------------------------------
    # РАНЖИРОВАНИЕ РЕЗУЛЬТАТОВ
    # ---------------------------------------------------------
    def _rank(self, result: dict, query: str) -> int:
        """
        Простая система ранжирования:
        +3 если точное совпадение в заголовке
        +2 если частичное совпадение в заголовке
        +1 если совпадение в тексте
        """
        title = result["title"].lower()
        snippet = (result["snippet"] or "").lower()
        q = query.lower()

        score = 0
        if title == q:
            score += 3
        if q in title:
            score += 2
        if q in snippet:
            score += 1

        return score

    # ---------------------------------------------------------
    # СОЗДАНИЕ СНИППЕТА (КУСОЧКА ТЕКСТА)
    # ---------------------------------------------------------
    def _make_snippet(self, text: str | None, query: str, radius: int = 40) -> str | None:
        """
        Возвращает небольшой фрагмент текста вокруг найденного слова.
        Используется для отображения результата поиска.
        """
        if not text:
            return None

        text_lower = text.lower()
        q = query.lower()

        index = text_lower.find(q)
        if index == -1:
            return None

        start = max(0, index - radius)
        end = min(len(text), index + len(query) + radius)

        snippet = text[start:end].replace("\n", " ")

        return snippet + "..."
