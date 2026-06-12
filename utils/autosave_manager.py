# utils/autosave_manager.py
"""
AutosaveManager — менеджер автосохранения заметок.

Реализует:
- автоматическое сохранение при изменении текста
- защиту от слишком частых сохранений (debounce)
- сохранение только при реальном изменении
- безопасную работу с NoteController

Используется в note_editor_view.py.
"""

from PySide6.QtCore import QTimer


class AutosaveManager:
    """
    Менеджер автосохранения.
    Привязывается к текстовому редактору и вызывает autosave() с задержкой.
    """

    def __init__(self, note_id: int, delay_ms: int = 800):
        self.note_id = note_id
        self.delay_ms = delay_ms

        # Ленивая инициализация
        self._controller = None

        # Последнее сохранённое содержимое
        self.last_saved_text = ""

        # Таймер для debounce
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._save)

    @property
    def controller(self):
        if self._controller is None:
            from controllers.note_controller import NoteController
            self._controller = NoteController()
        return self._controller

    # ---------------------------------------------------------
    # ПРИВЯЗКА К ТЕКСТОВОМУ ПОЛЮ
    # ---------------------------------------------------------
    def connect_editor(self, editor):
        """Подключает autosave к QTextEdit / QPlainTextEdit."""
        editor.textChanged.connect(lambda: self.schedule_save(editor))

    # ---------------------------------------------------------
    # ЗАПЛАНИРОВАТЬ СОХРАНЕНИЕ
    # ---------------------------------------------------------
    def schedule_save(self, editor):
        """Запускает таймер с задержкой."""
        self.current_editor = editor
        self.timer.start(self.delay_ms)

    # ---------------------------------------------------------
    # ВЫПОЛНИТЬ СОХРАНЕНИЕ
    # ---------------------------------------------------------
    def _save(self):
        """Сохраняет заметку, если текст изменился."""
        text = self.current_editor.toPlainText()

        # Если текст не изменился — ничего не делаем
        if text == self.last_saved_text:
            return

        # Сохраняем
        self.controller.autosave(self.note_id, text)

        # Обновляем состояние
        self.last_saved_text = text

    # ---------------------------------------------------------
    # РУЧНОЕ СОХРАНЕНИЕ (например, при закрытии окна)
    # ---------------------------------------------------------
    def force_save(self, editor):
        """Принудительное сохранение."""
        text = editor.toPlainText()
        self.controller.autosave(self.note_id, text)
        self.last_saved_text = text