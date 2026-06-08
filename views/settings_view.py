from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SettingsView(QWidget):
    """
    Экран настроек.
    """

    def __init__(self, settings_controller, parent=None):
        super().__init__(parent)
        self.settings_controller = settings_controller

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Настройки"))

    def refresh(self):
        """Загрузка текущих настроек."""
        pass
