# views/review_session_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QProgressBar, QSizePolicy, QSpacerItem, QScrollArea
)
from widgets.silent_message_box import QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from controllers.review_controller import ReviewController


class ReviewSessionView(QWidget):
    """Окно сессии повторения (галерея карточек)"""

    session_finished = Signal()
    back_to_cards = Signal()

    def __init__(self, flashcard_controller, topic_controller, parent=None):
        super().__init__(parent)
        self.flashcard_controller = flashcard_controller
        self.topic_controller = topic_controller
        self.review_controller = ReviewController()

        self.current_card = None
        self.showing_answer = False
        self.card_start_time = 0

        self.setup_ui()

    def setup_ui(self):
        # Главный layout с адаптивными отступами
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        # Отступы зависят от размера окна (проценты)
        layout.setContentsMargins(20, 15, 20, 15)

        # ========== Верхняя панель ==========
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        self.back_btn = QPushButton("← Назад")
        self.back_btn.setFixedWidth(80)
        self.back_btn.setFixedHeight(32)
        self.back_btn.clicked.connect(self._confirm_exit)
        top_layout.addWidget(self.back_btn)

        top_layout.addStretch()

        # Прогресс
        self.progress_label = QLabel("Карточка 0 из 0")
        self.progress_label.setStyleSheet("font-size: 12px; color: #666;")
        top_layout.addWidget(self.progress_label)

        layout.addLayout(top_layout)

        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #E0E0E0;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Небольшой отступ после прогресс-бара
        layout.addSpacing(15)

        # ========== Карточка (растягивается) ==========
        self.card_frame = QFrame()
        self.card_frame.setFrameShape(QFrame.Box)
        self.card_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.card_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #DDD;
                border-radius: 16px;
                background-color: white;
            }
        """)

        self.card_layout = QVBoxLayout(self.card_frame)
        self.card_layout.setSpacing(15)
        self.card_layout.setContentsMargins(25, 20, 25, 20)

        layout.addWidget(self.card_frame, 1)  # 1 = растягивается

        # ========== Кнопки оценки ==========
        rating_widget = QWidget()
        rating_widget.setFixedHeight(55)
        self.rating_layout = QHBoxLayout(rating_widget)
        self.rating_layout.setSpacing(12)
        self.rating_layout.setContentsMargins(0, 0, 0, 0)

        self.forgot_btn = QPushButton("😞 Забыл")
        self.forgot_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.forgot_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #D32F2F; }
            QPushButton:disabled { 
                background-color: #EF9A9A;
                color: #FFE0E0;
            }
        """)
        self.forgot_btn.clicked.connect(lambda: self._rate_card(1))

        self.hard_btn = QPushButton("🤔 Слабо")
        self.hard_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.hard_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #F57C00; }
            QPushButton:disabled { 
                background-color: #FFCC80;
                color: #FFE0B2;
            }
        """)
        self.hard_btn.clicked.connect(lambda: self._rate_card(2))

        self.good_btn = QPushButton("😊 Знаю")
        self.good_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.good_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { 
                background-color: #A5D6A7;
                color: #C8E6C9;
            }
        """)
        self.good_btn.clicked.connect(lambda: self._rate_card(3))

        self.rating_layout.addWidget(self.forgot_btn)
        self.rating_layout.addWidget(self.hard_btn)
        self.rating_layout.addWidget(self.good_btn)

        layout.addWidget(rating_widget)

        # Изначально кнопки оценки скрыты
        self._set_rating_buttons_enabled(False)

    def start_session(self, topic_ids: list, include_free: bool, include_qa: bool, skip_reviewed: bool = False):
        """Начинает новую сессию повторения"""
        cards = self.review_controller.start_session(topic_ids, include_free, include_qa, skip_reviewed)

        if not cards:
            QMessageBox.information(self, "Нет карточек", "Нет карточек для повторения в выбранных темах!")
            self.back_to_cards.emit()
            return

        self._update_progress()
        self._show_current_card()

    def _show_current_card(self):
        """Показывает текущую карточку"""
        self.current_card = self.review_controller.get_current_card()

        if not self.current_card or self.review_controller.is_session_complete():
            self._finish_session()
            return

        # Сбрасываем состояние
        self.showing_answer = False
        self._set_rating_buttons_enabled(False)

        # Запоминаем время начала показа
        from time import time
        self.card_start_time = time()

        # Очищаем карточку
        self._clear_card_layout()

        # Отображаем карточку в зависимости от типа
        if self.current_card.type == "free":
            self._show_free_card()
        else:
            self._show_qa_card()

        self._update_progress()

    def _clear_card_layout(self):
        """Очищает содержимое карточки"""
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_free_card(self):
        """Показывает свободную карточку"""
        self._set_rating_buttons_enabled(True)

        content_label = QLabel(self.current_card.content or "Нет содержимого")
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignCenter)
        content_label.setFont(QFont("Segoe UI", 16))
        content_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_label.setStyleSheet("""
            QLabel {
                padding: 25px;
                background-color: #F8F9FA;
                border-radius: 12px;
            }
        """)
        self.card_layout.addWidget(content_label)

    def _show_qa_card(self):
        """Показывает карточку Вопрос-Ответ"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        # Вопрос
        question_content = QLabel(self.current_card.question)
        question_content.setWordWrap(True)
        question_content.setAlignment(Qt.AlignCenter)
        question_content.setFont(QFont("Segoe UI", 16))
        question_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        question_content.setStyleSheet("""
            QLabel {
                padding: 20px;
                background-color: #F8F9FA;
                border-radius: 12px;
            }
        """)
        self.card_layout.addWidget(question_content)

        self.card_layout.addSpacing(10)

        # Кнопка показа ответа
        self.show_answer_btn = QPushButton("📖 Показать ответ")
        self.show_answer_btn.setFixedHeight(40)
        self.show_answer_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.show_answer_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        self.show_answer_btn.clicked.connect(self._toggle_answer)
        self.card_layout.addWidget(self.show_answer_btn, alignment=Qt.AlignCenter)

        # Контейнер для ответа
        self.answer_container = QWidget()
        self.answer_container.setVisible(False)
        answer_layout = QVBoxLayout(self.answer_container)
        answer_layout.setContentsMargins(0, 10, 0, 0)

        answer_content = QLabel(self.current_card.answer)
        answer_content.setWordWrap(True)
        answer_content.setAlignment(Qt.AlignCenter)
        answer_content.setFont(QFont("Segoe UI", 14))
        answer_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        answer_content.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #E8F5E9;
                border-radius: 8px;
                color: #2E7D32;
            }
        """)
        answer_layout.addWidget(answer_content)

        self.card_layout.addWidget(self.answer_container)
        self.card_layout.addStretch()



    def _toggle_answer(self):
        """Показывает/скрывает ответ и включает кнопки оценки"""
        if not hasattr(self, 'show_answer_btn') or not hasattr(self, 'answer_container'):
            return

        if self.showing_answer:
            self.answer_container.setVisible(False)
            self.show_answer_btn.setText("📖 Показать ответ")
            self.showing_answer = False
            self._set_rating_buttons_enabled(False)
        else:
            self.answer_container.setVisible(True)
            self.show_answer_btn.setText("📖 Скрыть ответ")
            self.showing_answer = True
            self._set_rating_buttons_enabled(True)

    def _rate_card(self, rating: int):
        """Оценивает карточку"""
        from time import time
        response_time = int(time() - self.card_start_time)

        self.review_controller.answer_card(rating, response_time)
        self._show_current_card()

    def _update_progress(self):
        """Обновляет отображение прогресса"""
        progress = self.review_controller.get_progress()
        current = progress['completed'] + 1
        total = progress['total']
        self.progress_label.setText(f"Карточка {current} из {total}")
        if total > 0:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(progress['completed'])

    def _set_rating_buttons_enabled(self, enabled: bool):
        """Включает/выключает кнопки оценки"""
        self.forgot_btn.setEnabled(enabled)
        self.hard_btn.setEnabled(enabled)
        self.good_btn.setEnabled(enabled)

    def _finish_session(self):
        """Завершает сессию и показывает результат"""
        self.review_controller.finish_session()

        stats = self.review_controller.get_progress()

        QMessageBox.information(
            self,
            "Сессия завершена!",
            f"🎉 Вы повторили {stats['completed']} из {stats['total']} карточек!\n\n"
            f"Нажмите «OK», чтобы вернуться к выбору тем."
        )

        self.back_to_cards.emit()

    def _confirm_exit(self):
        """Подтверждение выхода из сессии"""
        if not self.review_controller.is_session_complete():
            reply = QMessageBox.question(
                self,
                "Выйти из сессии?",
                "Вы не завершили повторение. Весь прогресс будет потерян.\n\n"
                "Вы уверены?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        self.back_to_cards.emit()