from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class DashboardView(QWidget):
    """
    Главный экран.
    Получает:
    - analytics_controller
    - session_controller
    """

    def __init__(self, analytics_controller, session_controller, parent=None):
        super().__init__(parent)

        self.analytics = analytics_controller
        self.session = session_controller

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Главная панель"))
        layout.addWidget(QLabel("Здесь будет статистика и текущая сессия"))

    def refresh(self):
        """Обновление данных при открытии."""
        pass
