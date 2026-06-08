from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class FocusSetupView(QWidget):
    """
    Экран настройки фокус-сессии.
    """

    def __init__(self, session_controller, settings_controller, parent=None):
        super().__init__(parent)
        self.session_controller = session_controller
        self.settings_controller = settings_controller

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Настройка фокус-сессии"))

        self.btn_start = QPushButton("Начать сессию")
        layout.addWidget(self.btn_start)

        # Позже: сюда можно пробросить callback из MainWindow
        # self.btn_start.clicked.connect(...)
    def refresh(self):
        """Обновление настроек по умолчанию."""
        pass
