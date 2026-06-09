# views/topic_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QTextEdit, QListWidget, QPushButton
)
from PySide6.QtCore import Qt, Signal


class TopicView(QWidget):
    back_requested = Signal()

    def __init__(self, topic_id: int, topic_controller, note_controller,
                 flashcard_controller, task_controller, session_controller,
                 parent=None):
        super().__init__(parent)
        self.topic_id = topic_id
        self.topic_controller = topic_controller
        self.note_controller = note_controller
        self.flashcard_controller = flashcard_controller
        self.task_controller = task_controller
        self.session_controller = session_controller

        # Загружаем тему
        self.topic = self.topic_controller.get_topic(topic_id)

        # Получаем или создаём заметку по умолчанию для этой темы
        self.current_note = self.note_controller.get_or_create_default_note(topic_id)

        # Основной лэйаут
        layout = QVBoxLayout(self)

        # ========== Верхняя панель с кнопкой "Назад" ==========
        top_bar = QHBoxLayout()
        self.back_button = QPushButton("← Назад к темам")
        self.back_button.clicked.connect(self.back_requested.emit)
        top_bar.addWidget(self.back_button)
        top_bar.addStretch()

        title_label = QLabel(self.topic.name)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        top_bar.addWidget(title_label)
        top_bar.addStretch()

        if hasattr(self.topic, 'updated_at') and self.topic.updated_at:
            date_label = QLabel(f"Изменено: {self.topic.updated_at[:16]}")
            date_label.setStyleSheet("color: gray; font-size: 12px;")
            top_bar.addWidget(date_label)

        layout.addLayout(top_bar)

        # ========== Вкладки ==========
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # ---------------------------------------------------------
        # Вкладка "Заметки" — с сохранением
        # ---------------------------------------------------------
        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)

        self.notes_editor = QTextEdit()
        self.notes_editor.setPlainText(self.current_note.content if self.current_note.content else "")
        self.notes_editor.textChanged.connect(self._auto_save_note)
        notes_layout.addWidget(self.notes_editor)

        self.save_status = QLabel("Сохранено")
        self.save_status.setStyleSheet("color: green; font-size: 10px;")
        notes_layout.addWidget(self.save_status)

        self.tabs.addTab(notes_widget, "📝 Заметки")

        # ---------------------------------------------------------
        # Вкладка "Карточки" (заглушка)
        # ---------------------------------------------------------
        cards_widget = QListWidget()
        cards_widget.addItem("Здесь будут карточки")
        self.tabs.addTab(cards_widget, "🃏 Карточки")

        # Вкладка "Задачи" (заглушка)
        tasks_widget = QListWidget()
        tasks_widget.addItem("Здесь будут задачи")
        self.tabs.addTab(tasks_widget, "✅ Задачи")

        # Вкладка "Сессии" (заглушка)
        sessions_widget = QListWidget()
        sessions_widget.addItem("Здесь будут сессии")
        self.tabs.addTab(sessions_widget, "⏱ Сессии")

        # Вкладка "Аналитика" (заглушка)
        analytics_widget = QLabel("Здесь будет аналитика по теме")
        analytics_widget.setAlignment(Qt.AlignCenter)
        self.tabs.addTab(analytics_widget, "📊 Аналитика")

        # Таймер для отложенного сохранения (чтобы не сохранять после каждого символа)
        self._save_timer = None

    # ---------------------------------------------------------
    # Автосохранение заметки
    # ---------------------------------------------------------
    def _auto_save_note(self):
        """Откладывает сохранение на 0.5 секунды после последнего изменения."""
        if self._save_timer:
            self._save_timer.stop()

        from PySide6.QtCore import QTimer
        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._save_note)
        self._save_timer.start(500)  # 0.5 секунды

    def _save_note(self):
        """Сохраняет текущее содержимое заметки в БД."""
        content = self.notes_editor.toPlainText()
        self.note_controller.update_note(self.current_note.id, content=content)
        self.save_status.setText("Сохранено")
        self.save_status.setStyleSheet("color: green; font-size: 10px;")
        # Сброс статуса через 2 секунды
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.save_status.setText(""))