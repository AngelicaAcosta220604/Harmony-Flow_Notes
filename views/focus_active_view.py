from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class FocusActiveView(QWidget):
    """
    Экран активной фокус-сессии.
    """

    def __init__(self, session_controller, note_controller, parent=None):
        super().__init__(parent)
        self.session_controller = session_controller
        self.note_controller = note_controller

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Активная фокус-сессия"))

    def refresh(self):
        """Обновление состояния сессии."""
        pass
