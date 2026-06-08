from PySide6.QtWidgets import QWidget, QVBoxLayout

class BaseView(QWidget):
    """
    Базовый класс для всех экранов.
    Содержит вертикальный layout и метод refresh().
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

    def refresh(self):
        """Обновление данных на экране."""
        pass
