# widgets/note_reader.py

from PySide6.QtWidgets import QTextBrowser, QWidget, QVBoxLayout
from PySide6.QtCore import Qt


class NoteReader(QWidget):
    """Виджет для отображения заметок с форматированием (read-only)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.browser.setStyleSheet("""
            QTextBrowser {
                border: none;
                padding: 10px;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self.browser)

    def set_html(self, html: str):
        """Устанавливает HTML содержимое"""
        if html:
            self.browser.setHtml(html)
        else:
            self.browser.clear()

    def set_plain_text(self, text: str):
        """Устанавливает plain text содержимое"""
        self.browser.setPlainText(text)

    def clear(self):
        self.browser.clear()