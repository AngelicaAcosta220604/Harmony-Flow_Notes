# views/main_window.py

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame,
)
from widgets.silent_dialog import SilentMessageBox
from PySide6.QtCore import Qt
from datetime import datetime

from views.flashcards_view import FlashcardsView
from widgets.tree_widget import TreeWidget
from views.focus_active_view import FocusActiveView
from controllers.topic_controller import TopicController
from controllers.note_controller import NoteController
from controllers.flashcard_controller import FlashcardController
from controllers.task_controller import TaskController
from controllers.session_controller import SessionController
from views.topic_view import TopicView
from utils.ping_manager import PingManager

from views.global_cards_view import GlobalCardsView
from views.review_session_view import ReviewSessionView


class MainWindow(QMainWindow):
    def __init__(self, topic_controller: TopicController,
                 note_controller: NoteController,
                 flashcard_controller: FlashcardController,
                 task_controller: TaskController,
                 session_controller: SessionController):
        super().__init__()
        self.topic_controller = topic_controller
        self.note_controller = note_controller
        self.flashcard_controller = flashcard_controller
        self.task_controller = task_controller
        self.session_controller = session_controller

        self.setWindowTitle("HFlow - Harmony & Flow Notes")
        self.setGeometry(100, 100, 1200, 800)

        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ================== Левый сайдбар ==================
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("background-color: #2C3E50; color: white;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignTop)

        btn_home = QPushButton("🏠 Главная")
        btn_topics = QPushButton("📚 Темы")
        btn_focus = QPushButton("⏱ Фокус")
        btn_tasks = QPushButton("✅ Задачи")
        btn_cards = QPushButton("🃏 Карточки")
        btn_analytics = QPushButton("📊 Аналитика")
        btn_settings = QPushButton("⚙ Настройки")

        btn_style = """
            QPushButton {
                text-align: left;
                padding: 12px;
                font-size: 14px;
                border: none;
                color: white;
            }
            QPushButton:hover {
                background-color: #34495E;
            }
        """
        for btn in [btn_home, btn_topics, btn_focus, btn_tasks, btn_cards, btn_analytics, btn_settings]:
            btn.setStyleSheet(btn_style)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # ================== Правая область (StackedWidget) ==================
        self.stack = QStackedWidget()

        # Страница 0: Главная
        page_home = QLabel("🏠 Главная страница\n\nДобро пожаловать в HFlow!")
        page_home.setAlignment(Qt.AlignCenter)
        page_home.setStyleSheet("font-size: 20px;")

        # Страница 1: Дерево тем
        self.tree_widget = TreeWidget(topic_controller=self.topic_controller)
        self.tree_widget.topic_selected.connect(self.on_topic_selected)
        self.tree_widget.topics_changed.connect(self.on_topics_changed)

        # Страница 2: Экран выбора темы для сессии
        self.focus_setup_view = self._create_focus_setup_view()

        # Страница 3: Экран активной сессии
        self.focus_active_view = FocusActiveView(
            session_controller=self.session_controller,
            note_controller=self.note_controller,
            topic_controller=self.topic_controller
        )
        self.focus_active_view.session_ended.connect(self.on_session_ended)
        self.focus_active_view.back_to_topics.connect(lambda: self.stack.setCurrentIndex(1))

        # Страница 4: Задачи
        page_tasks = QLabel("✅ Задачи\n\nСписок задач с дедлайнами")
        page_tasks.setAlignment(Qt.AlignCenter)

        # ================== Страницы карточек ==================
        # Страница 5: Глобальные карточки (выбор тем)
        self.global_cards_view = GlobalCardsView(
            flashcard_controller=self.flashcard_controller,
            topic_controller=self.topic_controller
        )
        self.global_cards_view.start_review_requested.connect(self.start_review_session)
        self.global_cards_view.cards_updated.connect(self.refresh_global_cards)

        # Страница 6: Сессия повторения
        self.review_session_view = ReviewSessionView(
            flashcard_controller=self.flashcard_controller,
            topic_controller=self.topic_controller
        )
        self.review_session_view.back_to_cards.connect(lambda: self.stack.setCurrentWidget(self.global_cards_view))
        self.review_session_view.session_finished.connect(self.refresh_global_cards)

        # Страница 7: Аналитика
        page_analytics = QLabel("📊 Аналитика\n\nГрафики и статистика")
        page_analytics.setAlignment(Qt.AlignCenter)

        # Страница 8: Настройки
        page_settings = QLabel("⚙ Настройки\n\nПараметры приложения")
        page_settings.setAlignment(Qt.AlignCenter)

        # Добавляем страницы
        self.stack.addWidget(page_home)                 # индекс 0
        self.stack.addWidget(self.tree_widget)          # индекс 1
        self.stack.addWidget(self.focus_setup_view)     # индекс 2
        self.stack.addWidget(self.focus_active_view)    # индекс 3
        self.stack.addWidget(page_tasks)                # индекс 4
        self.stack.addWidget(self.global_cards_view)    # индекс 5
        self.stack.addWidget(self.review_session_view)  # индекс 6
        self.stack.addWidget(page_analytics)            # индекс 7
        self.stack.addWidget(page_settings)             # индекс 8

        # ================== Собираем всё ==================
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, 1)

        # ================== Подключаем кнопки ==================
        btn_home.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_topics.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_focus.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        btn_tasks.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        btn_cards.clicked.connect(lambda: self.stack.setCurrentWidget(self.global_cards_view))
        btn_analytics.clicked.connect(lambda: self.stack.setCurrentIndex(7))
        btn_settings.clicked.connect(lambda: self.stack.setCurrentIndex(8))

        # ================== Настройка пинга ==================
        self.ping_manager = PingManager(idle_ms=15 * 60 * 1000)
        self.session_controller.set_ping_manager(self.ping_manager)
        self.session_controller.ping_needed.connect(self.show_ping_dialog)

    # ================== СОЗДАНИЕ ЭКРАНА ВЫБОРА ТЕМЫ ==================
    def _create_focus_setup_view(self):
        from PySide6.QtWidgets import QVBoxLayout, QComboBox, QPushButton, QLabel

        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("Выберите тему для фокус-сессии:"))

        self.session_topic_combo = QComboBox()
        self.refresh_topic_combo()
        layout.addWidget(self.session_topic_combo)

        btn_start = QPushButton("▶ Начать сессию")
        btn_start.clicked.connect(self.start_session_from_setup)
        layout.addWidget(btn_start)

        layout.addStretch()
        return widget

    def refresh_topic_combo(self):
        self.session_topic_combo.clear()
        topics = self.topic_controller.get_all_topics()
        for topic in topics:
            if topic.type == "topic":
                self.session_topic_combo.addItem(topic.name, topic.id)

    def start_session_from_setup(self):
        current_index = self.session_topic_combo.currentIndex()
        if current_index < 0:
            SilentMessageBox.warning(self, "Ошибка", "Сначала создайте хотя бы одну тему!")
            return

        topic_id = self.session_topic_combo.currentData()
        topic_name = self.session_topic_combo.currentText()

        self.focus_active_view.start_session(topic_id, topic_name)
        self.stack.setCurrentWidget(self.focus_active_view)

    def on_session_ended(self, session_id: int):
        self.stack.setCurrentIndex(2)
        self.refresh_topic_combo()
        self.tree_widget.load_topics()
        self.refresh_global_cards()

    def show_ping_dialog(self):
        from widgets.ping_dialog import PingDialog

        dialog = PingDialog(self)
        if dialog.exec():
            self.session_controller.user_responded_to_ping()

    # ================== ОБРАБОТКА ВЫБОРА ТЕМЫ ==================
    def on_topic_selected(self, topic_id: int):
        """Открывает выбранную тему"""
        topic_view = TopicView(
            topic_id=topic_id,
            topic_controller=self.topic_controller,
            note_controller=self.note_controller,
            flashcard_controller=self.flashcard_controller,
            task_controller=self.task_controller,
            session_controller=self.session_controller
        )
        topic_view.back_requested.connect(lambda: self.stack.setCurrentIndex(1))
        topic_view.start_session_requested.connect(self._start_session_from_topic)
        topic_view.resume_existing_session_requested.connect(self.resume_session_from_history)  # ← ДОБАВИТЬ
        topic_view.show_session_analytics.connect(self._show_session_analytics)
        topic_view.cards_updated.connect(self.refresh_global_cards)
        topic_view.topic_updated.connect(self.refresh_topic_combo)
        topic_view.topic_updated.connect(self.refresh_global_cards)
        self.stack.addWidget(topic_view)
        self.stack.setCurrentWidget(topic_view)

    def _start_session_from_topic(self, topic_id: int, topic_name: str):
        """Запускает сессию из темы"""
        self.stack.setCurrentIndex(2)
        index = self.session_topic_combo.findData(topic_id)
        if index >= 0:
            self.session_topic_combo.setCurrentIndex(index)

    def _show_session_analytics(self, session_id: int):
        """Показывает аналитику по сессии"""
        self.stack.setCurrentIndex(7)
        # TODO: передать session_id в AnalyticsView

    def start_review_session(self, topic_ids: list, include_free: bool, include_qa: bool, skip_reviewed: bool):
        self.review_session_view.start_session(topic_ids, include_free, include_qa, skip_reviewed)
        self.stack.setCurrentWidget(self.review_session_view)

    def refresh_global_cards(self):
        """Обновляет глобальную страницу карточек"""
        if hasattr(self, 'global_cards_view'):
            self.global_cards_view.refresh()

    def on_topics_changed(self):
        """Вызывается когда темы были изменены (созданы/удалены/переименованы/перемещены)"""
        self.refresh_topic_combo()
        self.refresh_global_cards()
        self.tree_widget.load_topics()

    # ================== ВОЗОБНОВЛЕНИЕ СЕССИИ ИЗ ИСТОРИИ ==================
    def resume_session_from_history(self, session_id: int, topic_name: str):
        """Возобновляет сессию из истории"""
        session = self.session_controller.get_session(session_id)
        if session:
            self.focus_active_view.resume_existing_session(session_id, session.topic_id, topic_name)
            self.stack.setCurrentWidget(self.focus_active_view)