# utils/export_manager.py
"""
ExportManager — менеджер экспорта данных в файлы.

Реализует:
- экспорт заметок в .txt
- экспорт карточек (free / qa)
- экспорт задач
- экспорт целой темы (папкой)
- безопасную работу с путями

Используется в UI: File → Export...
"""

from pathlib import Path


class ExportManager:

    def __init__(self):
        # Ленивая инициализация контроллеров
        self._notes = None
        self._flashcards = None
        self._tasks = None
        self._topics = None

    @property
    def notes(self):
        if self._notes is None:
            from controllers.note_controller import NoteController
            self._notes = NoteController()
        return self._notes

    @property
    def flashcards(self):
        if self._flashcards is None:
            from controllers.flashcard_controller import FlashcardController
            self._flashcards = FlashcardController()
        return self._flashcards

    @property
    def tasks(self):
        if self._tasks is None:
            from controllers.task_controller import TaskController
            self._tasks = TaskController()
        return self._tasks

    @property
    def topics(self):
        if self._topics is None:
            from controllers.topic_controller import TopicController
            self._topics = TopicController()
        return self._topics

    # ---------------------------------------------------------
    # ЭКСПОРТ ЗАМЕТКИ
    # ---------------------------------------------------------
    def export_note(self, note_id: int, folder: str) -> Path:
        """Экспортирует заметку в .txt файл."""
        note = self.notes.get_note(note_id)
        if not note:
            raise ValueError("Заметка не найдена")

        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)

        file_path = folder / f"{note.title}.txt"
        file_path.write_text(note.content or "", encoding="utf-8")

        return file_path

    # ---------------------------------------------------------
    # ЭКСПОРТ КАРТОЧКИ
    # ---------------------------------------------------------
    def export_flashcard(self, card_id: int, folder: str) -> Path:
        """Экспортирует карточку в .txt файл."""
        card = self.flashcards.get_flashcard(card_id)
        if not card:
            raise ValueError("Карточка не найдена")

        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)

        file_path = folder / f"flashcard_{card.id}.txt"

        if card.type == "qa":
            text = f"{card.question}\n---\n{card.answer}"
        else:
            text = card.question or ""

        file_path.write_text(text, encoding="utf-8")
        return file_path

    # ---------------------------------------------------------
    # ЭКСПОРТ ЗАДАЧИ
    # ---------------------------------------------------------
    def export_task(self, task_id: int, folder: str) -> Path:
        """Экспортирует задачу в .txt файл."""
        task = self.tasks.get_task(task_id)
        if not task:
            raise ValueError("Задача не найдена")

        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)

        file_path = folder / f"task_{task.id}.txt"
        text = f"TODO: {task.title}\n\n{task.description or ''}"
        file_path.write_text(text, encoding="utf-8")

        return file_path

    # ---------------------------------------------------------
    # ЭКСПОРТ ВСЕЙ ТЕМЫ (ПАПКОЙ)
    # ---------------------------------------------------------
    def export_topic(self, topic_id: int, folder: str) -> Path:
        """Экспортирует всю тему."""
        topic = self.topics.get_topic(topic_id)
        if not topic:
            raise ValueError("Тема не найдена")

        base = Path(folder)
        base.mkdir(parents=True, exist_ok=True)

        topic_folder = base / topic.name
        topic_folder.mkdir(exist_ok=True)

        # Экспорт заметок
        notes_folder = topic_folder / "notes"
        notes_folder.mkdir(exist_ok=True)
        for note in self.notes.get_notes_by_topic(topic_id):
            self.export_note(note.id, notes_folder)

        # Экспорт карточек
        flashcards_folder = topic_folder / "flashcards"
        flashcards_folder.mkdir(exist_ok=True)
        for card in self.flashcards.get_flashcards_by_topic(topic_id):
            self.export_flashcard(card.id, flashcards_folder)

        # Экспорт задач
        tasks_folder = topic_folder / "tasks"
        tasks_folder.mkdir(exist_ok=True)
        for task in self.tasks.get_tasks_by_topic(topic_id):
            self.export_task(task.id, tasks_folder)

        return topic_folder