# views/flashcards_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QComboBox, QDialog
)
from PySide6.QtCore import Qt, Signal
from widgets.silent_message_box import QMessageBox
from widgets.card_type_dialog import CardTypeDialog

class FlashcardsView(QWidget):
    """Виджет для отображения и управления карточками темы."""

    cards_updated = Signal()

    def __init__(self, flashcard_controller, topic_controller, topic_id: int = None, parent=None):
        super().__init__(parent)
        self.flashcard_controller = flashcard_controller
        self.topic_controller = topic_controller  # сохраняем
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
        if self.topic_id is None:
            # Глобальный режим: все карточки из всех тем
            self.current_cards = self.flashcard_controller.get_all_cards()
        else:
            # Режим конкретной темы
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
        """Создаёт виджет для одной карточки. Открывается по клику."""
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
                border-color: #999;
            }
        """)

        # Клик по карточке = открытие
        card_frame.mousePressEvent = lambda e, cid=card.id: self._open_card_dialog(cid)

        layout = QVBoxLayout(card_frame)
        layout.setSpacing(6)

        # ========== Верхняя строка: метка для Вопрос-Ответ + кнопка удаления ==========
        header_layout = QHBoxLayout()

        # Только для Вопрос-Ответ показываем маленькую метку
        if card.type == "qa":
            type_badge = QLabel("❓ Вопрос-Ответ")
            type_badge.setStyleSheet("""
                QLabel {
                    color: #1565C0;
                    font-size: 10px;
                    padding: 0px;
                    border: none;
                }
            """)
            header_layout.addWidget(type_badge)

        header_layout.addStretch()

        # Кнопка удаления
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(24, 24)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
                color: #999;
            }
            QPushButton:hover { color: #F44336; }
        """)
        delete_btn.setToolTip("Удалить")
        delete_btn.clicked.connect(lambda checked=False, cid=card.id: self.delete_card(cid))
        header_layout.addWidget(delete_btn)

        layout.addLayout(header_layout)

        # ========== Содержимое ==========
        if card.type == "free":
            content_label = QLabel(card.content or "Нет содержимого")
            content_label.setWordWrap(True)
            content_label.setStyleSheet("font-size: 13px; border: none; padding: 0px;")
            layout.addWidget(content_label)

        else:  # question_answer
            question_label = QLabel(f"<b>Вопрос:</b> {card.question}")
            question_label.setWordWrap(True)
            question_label.setStyleSheet("font-size: 13px; border: none; padding: 0px;")
            layout.addWidget(question_label)

        # ========== Дата (простая строка, без обводки) ==========
        date_str = ""
        if hasattr(card, 'updated_at') and card.updated_at:
            date_str = card.updated_at[:16]
        elif hasattr(card, 'created_at') and card.created_at:
            date_str = card.created_at[:16]

        if date_str:
            date_label = QLabel(date_str)
            date_label.setStyleSheet("color: #AAA; font-size: 10px; border: none; padding: 0px; margin-top: 5px;")
            layout.addWidget(date_label)

        if hasattr(card, 'review_status'):
            status_text = ""
            status_color = ""
            if card.review_status == "new":
                status_text = "🆕 Новое"
                status_color = "#9E9E9E"
            elif card.review_status == "learning":
                status_text = "📖 В процессе"
                status_color = "#FF9800"
            elif card.review_status == "review":
                status_text = "✅ Выучено"
                status_color = "#4CAF50"

            if status_text:
                status_label = QLabel(status_text)
                status_label.setStyleSheet(f"color: {status_color}; font-size: 10px; border: none; padding: 0px;")
                layout.addWidget(status_label)

        return card_frame


    def create_card(self):
        """Открывает диалог создания новой карточки."""
        dialog = CardTypeDialog("", self)
        if dialog.exec():
            if dialog.card_type == "free":
                content = dialog.get_free_content()
                if content:
                    # Определяем тему для карточки
                    if self.topic_id is None:
                        # Глобальный режим: нужно выбрать тему
                        from widgets.topic_selector_dialog import TopicSelectorDialog
                        topic_dialog = TopicSelectorDialog(self.topic_controller, self)
                        if topic_dialog.exec():
                            selected_topic_id = topic_dialog.get_selected_topic_id()
                            if selected_topic_id:
                                self.flashcard_controller.create_free_card(
                                    topic_id=selected_topic_id,
                                    content=content,
                                    source_note_id=None
                                )
                                QMessageBox.information(self, "Готово", "Свободная карточка создана!")
                                self.load_cards()
                                self.cards_updated.emit()
                            else:
                                return
                        else:
                            return
                    else:
                        # Режим конкретной темы
                        self.flashcard_controller.create_free_card(
                            topic_id=self.topic_id,
                            content=content,
                            source_note_id=None
                        )
                        QMessageBox.information(self, "Готово", "Свободная карточка создана!")
                        self.load_cards()
                else:
                    QMessageBox.warning(self, "Ошибка", "Содержание не может быть пустым")

            else:  # qa (вопрос-ответ)
                question = dialog.get_question()
                answer = dialog.get_answer()
                if question and answer:
                    # Определяем тему для карточки
                    if self.topic_id is None:
                        # Глобальный режим: нужно выбрать тему
                        from widgets.topic_selector_dialog import TopicSelectorDialog
                        topic_dialog = TopicSelectorDialog(self.topic_controller, self)
                        if topic_dialog.exec():
                            selected_topic_id = topic_dialog.get_selected_topic_id()
                            if selected_topic_id:
                                self.flashcard_controller.create_qa_card(
                                    topic_id=selected_topic_id,
                                    question=question,
                                    answer=answer,
                                    source_note_id=None
                                )
                                QMessageBox.information(self, "Готово", "Карточка Вопрос-Ответ создана!")
                                self.load_cards()
                            else:
                                return
                        else:
                            return
                    else:
                        # Режим конкретной темы
                        self.flashcard_controller.create_qa_card(
                            topic_id=self.topic_id,
                            question=question,
                            answer=answer,
                            source_note_id=None
                        )
                        QMessageBox.information(self, "Готово", "Карточка Вопрос-Ответ создана!")
                        self.load_cards()
                elif question and not answer:
                    # Нет ответа — спрашиваем пользователя
                    reply = QMessageBox.question(
                        self,
                        "Нет ответа",
                        "Вы не заполнили ответ.\n\n"
                        "• Нажмите «Да» — чтобы сохранить как свободную карточку\n"
                        "• Нажмите «Нет» — чтобы продолжить редактирование",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        # Сохраняем вопрос как свободную карточку
                        content = question
                        if self.topic_id is None:
                            from widgets.topic_selector_dialog import TopicSelectorDialog
                            topic_dialog = TopicSelectorDialog(self.topic_controller, self)
                            if topic_dialog.exec():
                                selected_topic_id = topic_dialog.get_selected_topic_id()
                                if selected_topic_id:
                                    self.flashcard_controller.create_free_card(
                                        topic_id=selected_topic_id,
                                        content=content,
                                        source_note_id=None
                                    )
                                    QMessageBox.information(self, "Готово", "Карточка сохранена как свободная!")
                                    self.load_cards()
                        else:
                            self.flashcard_controller.create_free_card(
                                topic_id=self.topic_id,
                                content=content,
                                source_note_id=None
                            )
                            QMessageBox.information(self, "Готово", "Карточка сохранена как свободная!")
                            self.load_cards()
                    # Если reply == QMessageBox.No — ничего не делаем, диалог остаётся открытым
                else:
                    QMessageBox.warning(self, "Ошибка", "Заполните хотя бы вопрос")

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

    def _toggle_answer(self, answer_widget, button):
        """Переключает видимость ответа и меняет текст кнопки."""
        if answer_widget.isVisible():
            answer_widget.setVisible(False)
            button.setText("📖 Показать ответ")
        else:
            answer_widget.setVisible(True)
            button.setText("📖 Скрыть ответ")

    def _open_card_dialog(self, card_id: int):
        """Открывает модальное окно с полным содержимым карточки."""
        # Находим карточку
        card = None
        for c in self.current_cards:
            if c.id == card_id:
                card = c
                break

        if not card:
            return

        # Создаём модальное окно
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Карточка #{card_id}")
        dialog.setMinimumSize(550, 450)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        # Заголовок с типом
        if card.type == "free":
            title_label = QLabel("📝 Свободная карточка")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
            layout.addWidget(title_label)

            # Содержимое с прокруткой
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("QScrollArea { border: none; }")

            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)

            content_label = QLabel(card.content or "Нет содержимого")
            content_label.setWordWrap(True)
            content_label.setStyleSheet("font-size: 14px; padding: 10px;")
            content_layout.addWidget(content_label)

            scroll.setWidget(content_widget)
            layout.addWidget(scroll)

        else:  # question_answer
            title_label = QLabel("❓ Карточка Вопрос-Ответ")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
            layout.addWidget(title_label)

            # Вопрос (всегда виден)
            question_frame = QFrame()
            question_frame.setStyleSheet("""
                QFrame {
                    background-color: #FFF3E0;
                    border-radius: 8px;
                    padding: 10px;
                    margin-top: 10px;
                }
            """)
            question_layout = QVBoxLayout(question_frame)
            question_layout.addWidget(QLabel("<b>Вопрос:</b>"))
            question_label = QLabel(card.question)
            question_label.setWordWrap(True)
            question_label.setStyleSheet("font-size: 14px;")
            question_layout.addWidget(question_label)
            layout.addWidget(question_frame)

            # Кнопка показа/скрытия ответа
            self.dialog_answer_widget = None  # для хранения ссылки
            self.dialog_toggle_btn = None

            toggle_btn = QPushButton("📖 Показать ответ")
            toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 13px;
                    margin-top: 10px;
                }
                QPushButton:hover { background-color: #45a049; }
            """)
            layout.addWidget(toggle_btn)

            # Контейнер для ответа (изначально скрыт)
            answer_container = QWidget()
            answer_container.setVisible(False)
            answer_container.setStyleSheet("""
                QWidget {
                    background-color: #E8F5E9;
                    border-radius: 8px;
                    padding: 10px;
                    margin-top: 10px;
                }
            """)
            answer_layout = QVBoxLayout(answer_container)
            answer_layout.addWidget(QLabel("<b>Ответ:</b>"))
            answer_label = QLabel(card.answer)
            answer_label.setWordWrap(True)
            answer_label.setStyleSheet("font-size: 14px;")
            answer_layout.addWidget(answer_label)
            layout.addWidget(answer_container)

            # Подключаем переключение
            def toggle_answer():
                if answer_container.isVisible():
                    answer_container.setVisible(False)
                    toggle_btn.setText("📖 Показать ответ")
                else:
                    answer_container.setVisible(True)
                    toggle_btn.setText("📖 Скрыть ответ")

            toggle_btn.clicked.connect(toggle_answer)

            layout.addStretch()

        # Кнопки внизу
        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("✏️ Редактировать")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFC107;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #FFB300; }
        """)
        edit_btn.clicked.connect(lambda: self._edit_from_dialog(card_id, dialog))

        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        close_btn.clicked.connect(dialog.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        dialog.exec()

    def _edit_from_dialog(self, card_id: int, dialog: QDialog):
        """Закрывает диалог и открывает редактирование карточки."""
        dialog.accept()
        self.edit_card(card_id)