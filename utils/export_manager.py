# managers/export_manager.py
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
from controllers.note_controller import NoteController
from controllers.flashcard_controller import FlashcardController
from controllers.task_controller import TaskController
from controllers.topic_controller import TopicController


class ExportManager:

    def __init__(self):
        self.notes = NoteController()
        self.flashcards = FlashcardController()
        self.tasks = TaskController()
        self.topics = TopicController()

    # ---------------------------------------------------------
    # ЭКСПОРТ ЗАМЕТКИ
    # ---------------------------------------------------------
    def export_note(self, note_id: int, folder: str) -> Path:
        """
        Экспортирует заметку в .txt файл.
        Возвращает путь к созданному файлу.
        """
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
        """
        Экспортирует карточку в .txt файл.
        Формат:
            Вопрос
            ---
            Ответ
        """
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
        """
        Экспортирует задачу в .txt файл.
        Формат:
            TODO: <title>
            <description>
        """
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
        """
        Экспортирует всю тему:
        - заметки
        - карточки
        - задачи
        Создаёт папку с названием темы.
        """
        topic = self.topics.get_topic(topic_id)
        if not topic:
            raise ValueError("Тема не найдена")

        base = Path(folder)
        base.mkdir(parents=True, exist_ok=True)

        topic_folder = base / topic.name
        topic_folder.mkdir(exist_ok=True)

        # Экспорт заметок
        for note in self.notes.get_notes_by_topic(topic_id):
            self.export_note(note.id, topic_folder / "notes")

        # Экспорт карточек
        for card in self.flashcards.get_flashcards_by_topic(topic_id):
            self.export_flashcard(card.id, topic_folder / "flashcards")

        # Экспорт задач
        for task in self.tasks.get_tasks_by_topic(topic_id):
            self.export_task(task.id, topic_folder / "tasks")

        return topic_folder
