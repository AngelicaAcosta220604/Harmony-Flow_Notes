from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class FlashcardsView(QWidget):
    """
    Экран карточек (повторение).
    """

    def __init__(self, flashcard_controller, parent=None):
        super().__init__(parent)
        self.flashcard_controller = flashcard_controller

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Карточки"))

    def refresh(self):
        """Обновление списка/сессии карточек."""
        pass
