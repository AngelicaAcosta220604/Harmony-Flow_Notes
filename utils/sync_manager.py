# managers/sync_manager.py
"""
SyncManager — менеджер синхронизации данных приложения.

Реализует:
- экспорт всех данных в JSON
- импорт данных из JSON
- частичную синхронизацию (по сущностям)
- безопасную работу с контроллерами
- возможность расширения до облачной синхронизации

Используется в настройках или вручную через UI.
"""

import json
from pathlib import Path
from datetime import datetime

from controllers.topic_controller import TopicController
from controllers.note_controller import NoteController
from controllers.task_controller import TaskController
from controllers.flashcard_controller import FlashcardController
from controllers.session_controller import SessionController


class SyncManager:

    def __init__(self):
        self.topics = TopicController()
        self.notes = NoteController()
        self.tasks = TaskController()
        self.flashcards = FlashcardController()
        self.sessions = SessionController()

    # ---------------------------------------------------------
    # ЭКСПОРТ ВСЕХ ДАННЫХ В JSON
    # ---------------------------------------------------------
    def export_all(self, file_path: str) -> Path:
        """
        Экспортирует ВСЕ данные приложения в один JSON-файл.
        """
        data = {
            "exported_at": datetime.now().isoformat(),
            "topics": [t.to_dict() for t in self.topics.get_all_topics()],
            "notes": [n.to_dict() for n in self.notes.get_all_notes()],
            "tasks": [t.to_dict() for t in self.tasks.get_all_tasks()],
            "flashcards": [c.to_dict() for c in self.flashcards.get_all_flashcards()],
            "sessions": [s.to_dict() for s in self.sessions.get_all_sessions()],
        }

        path = Path(file_path)
        path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
        return path

    # ---------------------------------------------------------
    # ИМПОРТ ВСЕХ ДАННЫХ ИЗ JSON
    # ---------------------------------------------------------
    def import_all(self, file_path: str):
        """
        Импортирует данные из JSON.
        НЕ удаляет существующие данные — только добавляет.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError("Файл синхронизации не найден")

        data = json.loads(path.read_text(encoding="utf-8"))

        # Темы
        for t in data.get("topics", []):
            self.topics.create_topic(t["name"])

        # Заметки
        for n in data.get("notes", []):
            self.notes.create_note(
                topic_id=n["topic_id"],
                title=n["title"],
                content=n["content"]
            )

        # Задачи
        for t in data.get("tasks", []):
            self.tasks.create_task(
                title=t["title"],
                description=t["description"],
                topic_id=t["topic_id"],
                deadline=t["deadline"],
                status=t["status"]
            )

        # Карточки
        for c in data.get("flashcards", []):
            self.flashcards.create_flashcard(
                topic_id=c["topic_id"],
                type=c["type"],
                question=c["question"],
                answer=c["answer"]
            )

        # Сессии
        for s in data.get("sessions", []):
            self.sessions._import_session_dict(s)

    # ---------------------------------------------------------
    # ЧАСТИЧНАЯ СИНХРОНИЗАЦИЯ
    # ---------------------------------------------------------
    def export_entity(self, entity_type: str, file_path: str):
        """
        Экспортирует одну сущность:
        - topics
        - notes
        - tasks
        - flashcards
        - sessions
        """
        match entity_type:
            case "topics":
                data = [t.to_dict() for t in self.topics.get_all_topics()]
            case "notes":
                data = [n.to_dict() for n in self.notes.get_all_notes()]
            case "tasks":
                data = [t.to_dict() for t in self.tasks.get_all_tasks()]
            case "flashcards":
                data = [c.to_dict() for c in self.flashcards.get_all_flashcards()]
            case "sessions":
                data = [s.to_dict() for s in self.sessions.get_all_sessions()]
            case _:
                raise ValueError(f"Неизвестный тип сущности: {entity_type}")

        path = Path(file_path)
        path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
        return path

    # ---------------------------------------------------------
    # ПРОВЕРКА СОВМЕСТИМОСТИ ФАЙЛА
    # ---------------------------------------------------------
    def validate_sync_file(self, file_path: str) -> bool:
        """
        Проверяет, что файл является корректным JSON-файлом синхронизации.
        """
        try:
            data = json.loads(Path(file_path).read_text(encoding="utf-8"))
            return "topics" in data or "notes" in data
        except:
            return False
