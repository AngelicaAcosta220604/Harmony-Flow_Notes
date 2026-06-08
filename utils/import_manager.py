# managers/import_manager.py
"""
ImportManager — менеджер импорта данных в приложение.

Реализует:
- импорт заметок из .txt
- импорт карточек (free / qa)
- импорт задач
- импорт целой папки
- автоматическое определение типа файла
- безопасная работа с путями

Используется в UI: File → Import...
"""

from pathlib import Path
from controllers.note_controller import NoteController
from controllers.flashcard_controller import FlashcardController
from controllers.task_controller import TaskController


class ImportManager:

    def __init__(self):
        self.notes = NoteController()
        self.flashcards = FlashcardController()
        self.tasks = TaskController()

    # ---------------------------------------------------------
    # ИМПОРТ ОДНОГО ФАЙЛА
    # ---------------------------------------------------------
    def import_file(self, file_path: str, topic_id: int) -> int | None:
        """
        Импортирует один файл.
        Возвращает id созданной сущности.
        """
        path = Path(file_path)

        if not path.exists() or not path.is_file():
            raise FileNotFoundError("Файл не найден")

        if path.suffix.lower() == ".txt":
            return self._import_txt(path, topic_id)

        raise ValueError(f"Неподдерживаемый формат файла: {path.suffix}")

    # ---------------------------------------------------------
    # ИМПОРТ ПАПКИ
    # ---------------------------------------------------------
    def import_folder(self, folder_path: str, topic_id: int) -> list[int]:
        """
        Импортирует все .txt файлы из папки.
        Возвращает список id созданных сущностей.
        """
        folder = Path(folder_path)

        if not folder.exists() or not folder.is_dir():
            raise NotADirectoryError("Папка не найдена")

        created_ids = []

        for file in folder.iterdir():
            if file.is_file() and file.suffix.lower() == ".txt":
                created_id = self._import_txt(file, topic_id)
                created_ids.append(created_id)

        return created_ids

    # ---------------------------------------------------------
    # ИМПОРТ .TXT
    # ---------------------------------------------------------
    def _import_txt(self, path: Path, topic_id: int) -> int:
        """
        Определяет тип файла и импортирует:
        - заметку
        - карточку (free / qa)
        - задачу
        """
        text = path.read_text(encoding="utf-8").strip()
        title = path.stem

        # 1) Попытка импортировать как карточку Q/A
        if "\n---\n" in text:
            parts = text.split("\n---\n", maxsplit=1)
            question = parts[0].strip()
            answer = parts[1].strip()
            return self.flashcards.create_flashcard(
                topic_id=topic_id,
                type="qa",
                question=question,
                answer=answer
            )

        # 2) Попытка импортировать как задачу (одна строка)
        if text.lower().startswith("todo:"):
            task_title = text[5:].strip()
            return self.tasks.create_task(
                title=task_title,
                description="Импортировано из файла",
                topic_id=topic_id
            )

        # 3) Иначе — импорт как заметки
        return self.notes.create_note(
            topic_id=topic_id,
            title=title,
            content=text
        )
