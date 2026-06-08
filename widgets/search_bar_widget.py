from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton

class SearchBarWidget(QWidget):
    """
    Строка поиска:
    - поле ввода
    - кнопка поиска
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Поиск...")
        self.layout.addWidget(self.input)

        self.button = QPushButton("Найти")
        self.layout.addWidget(self.button)

    def get_query(self) -> str:
        return self.input.text()
