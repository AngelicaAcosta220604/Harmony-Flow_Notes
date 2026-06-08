from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class TopicView(QWidget):
    """
    Экран конкретной темы:
    - краткая инфа
    - переход к заметкам / карточкам
    """

    def __init__(self, topic_controller, note_controller, flashcard_controller, parent=None):
        super().__init__(parent)
        self.topic_controller = topic_controller
        self.note_controller = note_controller
        self.flashcard_controller = flashcard_controller

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Экран темы"))

    def refresh(self):
        """Обновление данных по текущей теме."""
        pass
