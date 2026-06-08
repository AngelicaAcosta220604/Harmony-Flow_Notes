# managers/delete_manager.py
"""
DeleteManager — единый менеджер удаления сущностей.

Реализует:
- удаление тем (с каскадом)
- удаление заметок
- удаление задач
- удаление карточек
- удаление сессий (с логами и быстрыми заметками)
- безопасный интерфейс для UI

Используется в UI: при удалении любого объекта вызывается один метод.
"""

from controllers.topic_controller import TopicController
from controllers.note_controller import NoteController
from controllers.task_controller import TaskController
from controllers.flashcard_controller import FlashcardController
from controllers.session_controller import SessionController


class DeleteManager:

    def __init__(self):
        self.topic = TopicController()
        self.note = NoteController()
        self.task = TaskController()
        self.flashcard = FlashcardController()
        self.session = SessionController()

    # ---------------------------------------------------------
    # УДАЛЕНИЕ ПО ТИПУ
    # ---------------------------------------------------------
    def delete(self, entity_type: str, entity_id: int):
        """
        Универсальный метод удаления.
        entity_type:
            - "topic"
            - "note"
            - "task"
            - "flashcard"
            - "session"
        """
        match entity_type:
            case "topic":
                self.delete_topic(entity_id)
            case "note":
                self.delete_note(entity_id)
            case "task":
                self.delete_task(entity_id)
            case "flashcard":
                self.delete_flashcard(entity_id)
            case "session":
                self.delete_session(entity_id)
            case _:
                raise ValueError(f"Неизвестный тип сущности: {entity_type}")

    # ---------------------------------------------------------
    # УДАЛЕНИЕ ТЕМЫ (КАСКАДНО)
    # ---------------------------------------------------------
    def delete_topic(self, topic_id: int):
        """
        Удаляет тему и все связанные данные.
        Логика реализована в TopicController.
        """
        self.topic.delete_topic(topic_id)

    # ---------------------------------------------------------
    # УДАЛЕНИЕ ЗАМЕТКИ
    # ---------------------------------------------------------
    def delete_note(self, note_id: int):
        self.note.delete_note(note_id)

    # ---------------------------------------------------------
    # УДАЛЕНИЕ ЗАДАЧИ
    # ---------------------------------------------------------
    def delete_task(self, task_id: int):
        self.task.delete_task(task_id)

    # ---------------------------------------------------------
    # УДАЛЕНИЕ КАРТОЧКИ
    # ---------------------------------------------------------
    def delete_flashcard(self, card_id: int):
        self.flashcard.delete_flashcard(card_id)

    # ---------------------------------------------------------
    # УДАЛЕНИЕ СЕССИИ (С ЛОГАМИ И БЫСТРЫМИ ЗАМЕТКАМИ)
    # ---------------------------------------------------------
    def delete_session(self, session_id: int):
        self.session.delete_session(session_id)
