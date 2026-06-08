from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class TopicsView(QWidget):
    """
    Список тем / дерево тем.
    """

    def __init__(self, topic_controller, parent=None):
        super().__init__(parent)
        self.topic_controller = topic_controller

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Темы"))

    def refresh(self):
        """Обновление списка тем."""
        pass
