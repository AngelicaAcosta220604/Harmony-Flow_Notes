from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class NoteEditorView(QWidget):
    """
    Редактор заметок по теме.
    """

    def __init__(self, note_controller, flashcard_controller, parent=None):
        super().__init__(parent)
        self.note_controller = note_controller
        self.flashcard_controller = flashcard_controller

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Редактор заметок"))

    def refresh(self):
        """Обновление текста заметки / списка заметок."""
        pass
