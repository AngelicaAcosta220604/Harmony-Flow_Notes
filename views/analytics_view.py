from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class AnalyticsView(QWidget):
    """
    Экран аналитики.
    """

    def __init__(self, analytics_controller, parent=None):
        super().__init__(parent)
        self.analytics_controller = analytics_controller

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Аналитика"))

    def refresh(self):
        """Обновление графиков/метрик."""
        pass
