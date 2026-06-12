# utils/delete_manager.py
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


class DeleteManager:

    def __init__(self):
        # Ленивая инициализация контроллеров
        self._topic = None
        self._note = None
        self._task = None
        self._flashcard = None
        self._session = None

    @property
    def topic(self):
        if self._topic is None:
            from controllers.topic_controller import TopicController
            self._topic = TopicController()
        return self._topic

    @property
    def note(self):
        if self._note is None:
            from controllers.note_controller import NoteController
            self._note = NoteController()
        return self._note

    @property
    def task(self):
        if self._task is None:
            from controllers.task_controller import TaskController
            self._task = TaskController()
        return self._task

    @property
    def flashcard(self):
        if self._flashcard is None:
            from controllers.flashcard_controller import FlashcardController
            self._flashcard = FlashcardController()
        return self._flashcard

    @property
    def session(self):
        if self._session is None:
            from controllers.session_controller import SessionController
            self._session = SessionController()
        return self._session

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
        """Удаляет тему и все связанные данные."""
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