# views/flashcards_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, Signal
from widgets.card_type_dialog import CardTypeDialog


class FlashcardsView(QWidget):
    """Виджет для отображения и управления карточками темы."""

    cards_updated = Signal()

    def __init__(self, flashcard_controller, topic_id: int, parent=None):
        super().__init__(parent)
        self.flashcard_controller = flashcard_controller
        self.topic_id = topic_id

        self.current_cards = []
        self.current_filter = "all"  # all, free, qa

        self.setup_ui()
        self.load_cards()

    def setup_ui(self):
        """Настройка интерфейса."""
        layout = QVBoxLayout(self)

        # ========== Верхняя панель: кнопка создания + фильтр ==========
        top_bar = QHBoxLayout()

        self.create_btn = QPushButton("+ Создать карточку")
        self.create_btn.clicked.connect(self.create_card)
        top_bar.addWidget(self.create_btn)

        top_bar.addSpacing(20)

        # Фильтр по типу карточек
        filter_label = QLabel("Показать:")
        filter_label.setStyleSheet("font-size: 12px;")
        top_bar.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("📋 Все карточки", "all")
        self.filter_combo.addItem("📝 Свободные", "free")
        self.filter_combo.addItem("❓ Вопрос-Ответ", "qa")
        self.filter_combo.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #CCC;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
        """)
        self.filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        top_bar.addWidget(self.filter_combo)

        top_bar.addStretch()
        layout.addLayout(top_bar)

        # ========== Область для списка карточек ==========
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.cards_layout.setSpacing(10)

        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)

    def _on_filter_changed(self):
        """Обработчик изменения фильтра."""
        self.current_filter = self.filter_combo.currentData()
        self.display_cards()

    def load_cards(self):
        """Загружает карточки из БД."""
        self.current_cards = self.flashcard_controller.get_cards_by_topic(self.topic_id)
        self.display_cards()

    def display_cards(self):
        """Отображает карточки с учётом фильтра."""
        # Очищаем старые виджеты
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Фильтруем карточки
        if self.current_filter == "free":
            filtered_cards = [c for c in self.current_cards if c.type == "free"]
        elif self.current_filter == "qa":
            filtered_cards = [c for c in self.current_cards if c.type == "qa"]
        else:
            filtered_cards = self.current_cards

        if not filtered_cards:
            empty_label = QLabel("Нет карточек. Создайте первую!")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: gray; padding: 40px;")
            self.cards_layout.addWidget(empty_label)
            return

        for card in filtered_cards:
            card_widget = self._create_card_widget(card)
            self.cards_layout.addWidget(card_widget)

    def _create_card_widget(self, card):
        """Создаёт виджет для одной карточки (без текстового типа, только иконка)."""
        card_frame = QFrame()
        card_frame.setFrameShape(QFrame.Box)
        card_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #DDD;
                border-radius: 6px;
                padding: 10px;
                margin: 2px;
                background-color: white;
            }
            QFrame:hover {
                background-color: #F9F9F9;
            }
        """)

        layout = QVBoxLayout(card_frame)

        # ========== Верхняя строка: иконка + кнопки ==========
        header_layout = QHBoxLayout()

        # Иконка вместо текстового типа
        if card.type == "free":
            icon_label = QLabel("📝")
            icon_label.setStyleSheet("font-size: 18px;")
            content_preview = card.content[:100] + "..." if len(card.content or "") > 100 else card.content
        else:
            icon_label = QLabel("❓")
            icon_label.setStyleSheet("font-size: 18px;")
            content_preview = card.question[:100] + "..." if len(card.question or "") > 100 else card.question

        header_layout.addWidget(icon_label)
        header_layout.addSpacing(5)

        # Превью содержимого
        preview_label = QLabel(content_preview or "Нет содержимого")
        preview_label.setWordWrap(True)
        preview_label.setStyleSheet("color: #333; font-size: 13px;")
        preview_label.setMinimumWidth(200)
        header_layout.addWidget(preview_label, stretch=1)

        # Кнопка редактирования
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(28, 28)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFC107;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #FFB300; }
        """)
        edit_btn.setToolTip("Редактировать")
        edit_btn.clicked.connect(lambda checked=False, cid=card.id: self.edit_card(cid))
        header_layout.addWidget(edit_btn)

        # Кнопка удаления
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #D32F2F; }
        """)
        delete_btn.setToolTip("Удалить")
        delete_btn.clicked.connect(lambda checked=False, cid=card.id: self.delete_card(cid))
        header_layout.addWidget(delete_btn)

        layout.addLayout(header_layout)

        # ========== Дата ==========
        date_str = ""
        if hasattr(card, 'updated_at') and card.updated_at:
            date_str = card.updated_at[:16]
        elif hasattr(card, 'created_at') and card.created_at:
            date_str = card.created_at[:16]

        if date_str:
            date_label = QLabel(date_str)
            date_label.setStyleSheet("color: gray; font-size: 10px; margin-top: 5px;")
            layout.addWidget(date_label)

        return card_frame

    def create_card(self):
        """Открывает диалог создания новой карточки."""
        dialog = CardTypeDialog("", self)
        if dialog.exec():
            if dialog.card_type == "free":
                content = dialog.get_free_content()
                if content:
                    self.flashcard_controller.create_free_card(
                        topic_id=self.topic_id,
                        content=content,
                        source_note_id=None
                    )
                    QMessageBox.information(self, "Готово", "Свободная карточка создана!")
                    self.load_cards()
                else:
                    QMessageBox.warning(self, "Ошибка", "Содержание не может быть пустым")
            else:  # qa
                question = dialog.get_question()
                answer = dialog.get_answer()
                if question and answer:
                    self.flashcard_controller.create_qa_card(
                        topic_id=self.topic_id,
                        question=question,
                        answer=answer,
                        source_note_id=None
                    )
                    QMessageBox.information(self, "Готово", "Карточка Вопрос-Ответ создана!")
                    self.load_cards()
                else:
                    QMessageBox.warning(self, "Ошибка", "Заполните и вопрос, и ответ")

    def edit_card(self, card_id: int):
        """Редактирование существующей карточки."""
        card = next((c for c in self.current_cards if c.id == card_id), None)
        if not card:
            return

        if card.type == "free":
            dialog = CardTypeDialog(card.content, self)
            dialog._select_type("free")
            if dialog.exec():
                new_content = dialog.get_free_content()
                if new_content:
                    self.flashcard_controller.update_card(card_id, content=new_content)
                    QMessageBox.information(self, "Готово", "Карточка обновлена!")
                    self.load_cards()
                else:
                    QMessageBox.warning(self, "Ошибка", "Содержание не может быть пустым")
        else:  # question-answer
            dialog = CardTypeDialog("", self)
            dialog._select_type("qa")
            dialog.question_input.setText(card.question)
            dialog.answer_input.setPlainText(card.answer)
            if dialog.exec():
                new_question = dialog.get_question()
                new_answer = dialog.get_answer()
                if new_question and new_answer:
                    self.flashcard_controller.update_card(card_id, question=new_question, answer=new_answer)
                    QMessageBox.information(self, "Готово", "Карточка обновлена!")
                    self.load_cards()
                else:
                    QMessageBox.warning(self, "Ошибка", "Заполните и вопрос, и ответ")

    def delete_card(self, card_id: int):
        """Удаляет карточку после подтверждения."""
        reply = QMessageBox.question(
            self, "Удаление",
            "Вы уверены, что хотите удалить эту карточку?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.flashcard_controller.delete_card(card_id)
            self.load_cards()

    def refresh(self):
        """Обновляет список карточек."""
        self.load_cards()