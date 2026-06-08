from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class OnboardingWizard(QWidget):
    """
    Онбординг / первый запуск.
    """

    def __init__(self, settings_controller, parent=None):
        super().__init__(parent)
        self.settings_controller = settings_controller

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Онбординг"))

    def refresh(self):
        """Проверка состояния онбординга."""
        pass
