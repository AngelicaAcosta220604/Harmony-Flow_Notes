# utils/import_manager.py
"""
ImportManager — менеджер импорта данных в приложение.

Реализует:
- импорт заметок из .txt
- импорт карточек (free / qa)
- импорт задач
- импорт целой папки
- автоматическое определение типа файла
- безопасную работу с путями

Используется в UI: File → Import...
"""

from pathlib import Path


class ImportManager:

    def __init__(self):
        # Ленивая инициализация - контроллеры создаются только при первом использовании
        self._notes = None
        self._flashcards = None
        self._tasks = None

    @property
    def notes(self):
        """Ленивая загрузка контроллера заметок"""
        if self._notes is None:
            from controllers.note_controller import NoteController
            self._notes = NoteController()
        return self._notes

    @property
    def flashcards(self):
        """Ленивая загрузка контроллера карточек"""
        if self._flashcards is None:
            from controllers.flashcard_controller import FlashcardController
            self._flashcards = FlashcardController()
        return self._flashcards

    @property
    def tasks(self):
        """Ленивая загрузка контроллера задач"""
        if self._tasks is None:
            from controllers.task_controller import TaskController
            self._tasks = TaskController()
        return self._tasks

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
            raise FileNotFoundError(f"Файл не найден: {file_path}")

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
            raise NotADirectoryError(f"Папка не найдена: {folder_path}")

        created_ids = []

        for file in folder.iterdir():
            if file.is_file() and file.suffix.lower() == ".txt":
                try:
                    created_id = self._import_txt(file, topic_id)
                    created_ids.append(created_id)
                except Exception as e:
                    print(f"Ошибка при импорте {file.name}: {e}")
                    continue

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

        if not text:
            raise ValueError(f"Файл {path.name} пуст")

        title = path.stem

        # 1) Попытка импортировать как карточку Q/A
        if "\n---\n" in text:
            parts = text.split("\n---\n", maxsplit=1)
            question = parts[0].strip()
            answer = parts[1].strip() if len(parts) > 1 else ""

            if not question:
                raise ValueError(f"В файле {path.name} нет вопроса для карточки")

            return self.flashcards.create_flashcard(
                topic_id=topic_id,
                type="qa",
                question=question,
                answer=answer
            )

        # 2) Попытка импортировать как задачу (начинается с TODO:)
        if text.lower().startswith("todo:"):
            task_title = text[5:].strip()

            if not task_title:
                raise ValueError(f"В файле {path.name} нет названия задачи")

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

    # ---------------------------------------------------------
    # ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ДЛЯ УДОБСТВА
    # ---------------------------------------------------------
    def import_multiple_files(self, file_paths: list[str], topic_id: int) -> dict:
        """
        Импортирует несколько файлов.
        Возвращает словарь с результатами: {'success': [...], 'failed': [...]}
        """
        results = {'success': [], 'failed': []}

        for file_path in file_paths:
            try:
                entity_id = self.import_file(file_path, topic_id)
                results['success'].append({'file': file_path, 'id': entity_id})
            except Exception as e:
                results['failed'].append({'file': file_path, 'error': str(e)})

        return results

    def guess_file_type(self, file_path: str) -> str:
        """
        Определяет тип файла без импорта.
        Возвращает: 'note', 'flashcard_qa', 'task' или 'unknown'
        """
        path = Path(file_path)

        if not path.exists() or path.suffix.lower() != ".txt":
            return 'unknown'

        try:
            text = path.read_text(encoding="utf-8").strip()

            if "\n---\n" in text:
                return 'flashcard_qa'
            elif text.lower().startswith("todo:"):
                return 'task'
            else:
                return 'note'
        except:
            return 'unknown'