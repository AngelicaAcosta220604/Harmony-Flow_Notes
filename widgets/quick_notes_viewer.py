# widgets/quick_notes_viewer.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QWidget, QMessageBox
)
from PySide6.QtCore import Qt
from widgets.silent_dialog import SilentMessageBox
from services import TimeService


class QuickNotesViewer(QDialog):
    """Окно для просмотра и удаления быстрых записей сессии"""

    def __init__(self, session_controller, session_id: int, parent=None):
        super().__init__(parent)
        self.session_controller = session_controller
        self.session_id = session_id

        self.setWindowTitle(f"Быстрые записи сессии #{session_id}")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.resize(550, 450)

        self.setup_ui()
        self.load_notes()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Заголовок
        title_label = QLabel("📝 Быстрые записи во время сессии")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        # Скролл-область для списка записей
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #DDD;
                border-radius: 6px;
                background-color: #FAFAFA;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #F0F0F0;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #CCC;
                border-radius: 4px;
                min-height: 20px;
            }
        """)

        self.notes_container = QWidget()
        self.notes_layout = QVBoxLayout(self.notes_container)
        self.notes_layout.setAlignment(Qt.AlignTop)
        self.notes_layout.setSpacing(8)
        self.notes_layout.setContentsMargins(10, 10, 10, 10)

        self.scroll_area.setWidget(self.notes_container)
        layout.addWidget(self.scroll_area)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.setFixedSize(100, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        close_btn.clicked.connect(self.accept)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def load_notes(self):
        """Загружает и отображает быстрые записи"""
        # Очищаем контейнер
        while self.notes_layout.count():
            item = self.notes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        notes = self.session_controller.get_quick_notes(self.session_id)

        if not notes:
            empty_label = QLabel("Нет быстрых записей во время этой сессии")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #999; font-size: 13px; padding: 40px;")
            self.notes_layout.addWidget(empty_label)
            return

        for note in notes:
            note_widget = self._create_note_widget(note)
            self.notes_layout.addWidget(note_widget)

    def _create_note_widget(self, note):
        """Создаёт виджет для одной заметки"""
        note_frame = QFrame()
        note_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #E0E0E0;
                background-color: white;
                border-radius: 6px;
                padding: 8px;
            }
            QFrame:hover {
                background-color: #F9F9F9;
                border-color: #CCC;
            }
        """)

        layout = QVBoxLayout(note_frame)
        layout.setSpacing(6)

        # Верхняя строка: дата и кнопка удаления
        header_layout = QHBoxLayout()

        if note.created_at:
            date_str = TimeService.format_display(note.created_at)
            if date_str:
                date_label = QLabel(f"📌 {date_str}")
                date_label.setStyleSheet("color: #666; font-size: 11px;")
                header_layout.addWidget(date_label)

        header_layout.addStretch()

        # Кнопка удаления
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(24, 24)
        delete_btn.setToolTip("Удалить запись")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 13px;
                color: #999;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
        """)
        delete_btn.clicked.connect(lambda checked, nid=note.id: self._delete_note(nid))
        header_layout.addWidget(delete_btn)

        layout.addLayout(header_layout)

        # Текст заметки
        text_label = QLabel(note.content)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("color: #333; font-size: 13px;")
        layout.addWidget(text_label)

        return note_frame

    def _delete_note(self, note_id: int):
        """Удаляет заметку с подтверждением"""
        reply = SilentMessageBox.question(
            self,
            "Удаление записи",
            "Вы уверены, что хотите удалить эту быструю запись?"
        )
        if reply == QMessageBox.Yes:
            from database.db_manager import db
            db.execute("DELETE FROM quick_notes WHERE id = ?", (note_id,))
            self.load_notes()  # Обновляем список