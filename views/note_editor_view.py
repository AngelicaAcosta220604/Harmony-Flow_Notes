# views/note_editor_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QMessageBox, QDialog  # QDialog добавлен!
)
from PySide6.QtCore import Qt, Signal, QTimer
from widgets.rich_text_editor import RichTextEditor
from widgets.card_type_dialog import CardTypeDialog
from widgets.task_dialog import TaskDialog


class NoteEditorView(QWidget):
    """Окно редактирования заметки с полноценным редактором"""

    note_saved = Signal(int)
    back_requested = Signal()

    def __init__(self, note_controller, flashcard_controller, task_controller, parent=None):
        super().__init__(parent)
        self.note_controller = note_controller
        self.flashcard_controller = flashcard_controller
        self.task_controller = task_controller
        self.current_note_id = None
        self.current_topic_id = None
        self.current_title = ""
        self.card_dialog = None

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Верхняя панель
        top_bar = QHBoxLayout()

        self.back_btn = QPushButton("← Назад")
        self.back_btn.clicked.connect(self.back_requested.emit)
        top_bar.addWidget(self.back_btn)

        top_bar.addStretch()

        # Кнопки создания
        self.create_card_btn = QPushButton("🃏 Создать карточку")
        self.create_card_btn.clicked.connect(self._create_card_from_selection)
        top_bar.addWidget(self.create_card_btn)

        self.create_task_btn = QPushButton("✅ Создать задачу")
        self.create_task_btn.clicked.connect(self._create_task_from_selection)
        top_bar.addWidget(self.create_task_btn)

        self.save_btn = QPushButton("💾 Сохранить (Ctrl+S)")
        self.save_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        top_bar.addWidget(self.save_btn)

        layout.addLayout(top_bar)

        # Редактор
        self.editor = RichTextEditor()
        layout.addWidget(self.editor)

    def connect_signals(self):
        self.save_btn.clicked.connect(self.save_note)

    def load_note(self, note_id: int, topic_id: int):
        """Загружает заметку для редактирования"""
        self.current_note_id = note_id
        self.current_topic_id = topic_id

        note = self.note_controller.get_note(note_id)
        if note:
            self.current_title = note.title or "Без названия"
            content = note.content or ""
            if content.strip().startswith("<"):
                self.editor.set_html(content)
            else:
                self.editor.set_plain_text(content)

    def save_note(self):
        """Сохраняет заметку"""
        if not self.current_note_id:
            return

        content = self.editor.to_html()
        self.note_controller.update_note(self.current_note_id, content=content)

        self.save_btn.setText("✓ Сохранено!")
        QTimer.singleShot(1500, lambda: self.save_btn.setText("💾 Сохранить (Ctrl+S)"))

        self.note_saved.emit(self.current_note_id)

    # ==================== СОЗДАНИЕ КАРТОЧКИ ====================

    def _create_card_from_selection(self):
        """Создаёт карточку из выделенного текста (немодальный диалог)"""
        selected = self.editor.editor.textCursor().selectedText()
        if not selected:
            QMessageBox.information(self, "Нет выделения", "Выделите текст для создания карточки")
            return

        # Создаём НЕмодальный диалог
        self.card_dialog = CardTypeDialog(selected, self)
        self.card_dialog.finished.connect(self._on_card_dialog_finished)
        self.card_dialog.show()

    def _on_card_dialog_finished(self, result):
        """Обработчик закрытия диалога карточки"""
        if result == QDialog.Accepted and self.card_dialog:
            if self.card_dialog.card_type == "free":
                content = self.card_dialog.get_free_content()
                if content:
                    self.flashcard_controller.create_free_card(
                        topic_id=self.current_topic_id,
                        content=content,
                        source_note_id=self.current_note_id
                    )
                    QMessageBox.information(self, "Готово", "Свободная карточка создана!")
            else:  # qa
                question = self.card_dialog.get_question()
                answer = self.card_dialog.get_answer()

                if question and answer:
                    self.flashcard_controller.create_qa_card(
                        topic_id=self.current_topic_id,
                        question=question,
                        answer=answer,
                        source_note_id=self.current_note_id
                    )
                    QMessageBox.information(self, "Готово", "Карточка Вопрос-Ответ создана!")
                elif question and not answer:
                    # Сохраняем как свободную карточку
                    self.flashcard_controller.create_free_card(
                        topic_id=self.current_topic_id,
                        content=question,
                        source_note_id=self.current_note_id
                    )
                    QMessageBox.information(self, "Готово", "Сохранено как свободная карточка")

        if self.card_dialog:
            self.card_dialog.deleteLater()
            self.card_dialog = None

    # ==================== СОЗДАНИЕ ЗАДАЧИ ====================

    def _create_task_from_selection(self):
        """Создаёт задачу из выделенного текста"""
        selected = self.editor.editor.textCursor().selectedText()
        if not selected:
            QMessageBox.information(self, "Нет выделения", "Выделите текст для создания задачи")
            return

        dialog = TaskDialog(self)
        dialog.title_input.setText(selected[:100])

        if dialog.exec():
            title = dialog.get_title()
            description = dialog.get_description()
            deadline = dialog.get_deadline()

            if title:
                self.task_controller.create_task(
                    title=title,
                    description=description,
                    topic_id=self.current_topic_id,
                    deadline=deadline
                )
                QMessageBox.information(self, "Готово", f"Задача «{title}» создана!")
            else:
                QMessageBox.warning(self, "Ошибка", "Название задачи не может быть пустым")