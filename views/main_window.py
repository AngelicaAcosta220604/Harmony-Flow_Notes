# views/main_window.py

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame, QMessageBox,
)
from widgets.silent_dialog import SilentMessageBox
from PySide6.QtCore import Qt
from datetime import datetime

from views.flashcards_view import FlashcardsView
from widgets.tree_widget import TreeWidget
from views.focus_active_view import FocusActiveView
from views.focus_setup_view import FocusSetupView  # ← добавить импорт
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

        # ================== Правая область ==================
        self.stack = QStackedWidget()

        page_home = QLabel("🏠 Главная страница\n\nДобро пожаловать в HFlow!")
        page_home.setAlignment(Qt.AlignCenter)
        page_home.setStyleSheet("font-size: 20px;")

        self.tree_widget = TreeWidget(topic_controller=self.topic_controller)
        self.tree_widget.topic_selected.connect(self.on_topic_selected)
        self.tree_widget.topics_changed.connect(self.on_topics_changed)

        # Страница 2: Экран выбора темы для сессии (НОВЫЙ)
        self.focus_setup_view = FocusSetupView(
            session_controller=self.session_controller,
            settings_controller=None,
            topic_controller=self.topic_controller,
            parent=self
        )
        self.focus_setup_view.start_session_requested.connect(self._handle_session_start)
        self.focus_setup_view.resume_session_requested.connect(self.resume_session_from_history)

        # Страница 3: Экран активной сессии
        self.focus_active_view = FocusActiveView(
            session_controller=self.session_controller,
            note_controller=self.note_controller,
            topic_controller=self.topic_controller
        )
        self.focus_active_view.session_ended.connect(self.on_session_ended)
        self.focus_active_view.back_to_topics.connect(lambda: self.stack.setCurrentWidget(self.focus_setup_view))

        page_tasks = QLabel("✅ Задачи\n\nСписок задач с дедлайнами")
        page_tasks.setAlignment(Qt.AlignCenter)

        self.global_cards_view = GlobalCardsView(
            flashcard_controller=self.flashcard_controller,
            topic_controller=self.topic_controller
        )
        self.global_cards_view.start_review_requested.connect(self.start_review_session)
        self.global_cards_view.cards_updated.connect(self.refresh_global_cards)

        self.review_session_view = ReviewSessionView(
            flashcard_controller=self.flashcard_controller,
            topic_controller=self.topic_controller
        )
        self.review_session_view.back_to_cards.connect(lambda: self.stack.setCurrentWidget(self.global_cards_view))
        self.review_session_view.session_finished.connect(self.refresh_global_cards)

        page_analytics = QLabel("📊 Аналитика\n\nГрафики и статистика")
        page_analytics.setAlignment(Qt.AlignCenter)

        page_settings = QLabel("⚙ Настройки\n\nПараметры приложения")
        page_settings.setAlignment(Qt.AlignCenter)

        self.stack.addWidget(page_home)  # индекс 0
        self.stack.addWidget(self.tree_widget)  # индекс 1
        self.stack.addWidget(self.focus_setup_view)  # индекс 2
        self.stack.addWidget(self.focus_active_view)  # индекс 3
        self.stack.addWidget(page_tasks)  # индекс 4
        self.stack.addWidget(self.global_cards_view)  # индекс 5
        self.stack.addWidget(self.review_session_view)  # индекс 6
        self.stack.addWidget(page_analytics)  # индекс 7
        self.stack.addWidget(page_settings)  # индекс 8

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, 1)

        # ================== Подключаем кнопки ==================
        btn_home.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_topics.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_focus.clicked.connect(self._on_focus_clicked)  # ← изменено
        btn_tasks.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        btn_cards.clicked.connect(lambda: self.stack.setCurrentWidget(self.global_cards_view))
        btn_analytics.clicked.connect(lambda: self.stack.setCurrentIndex(7))
        btn_settings.clicked.connect(lambda: self.stack.setCurrentIndex(8))

        # ================== Настройка пинга ==================
        self.ping_manager = PingManager(idle_ms=15 * 60 * 1000)
        self.session_controller.set_ping_manager(self.ping_manager)
        self.session_controller.ping_needed.connect(self.show_ping_dialog)

    # ================== ЕДИНЫЙ МЕТОД ДЛЯ ЗАПУСКА/ВОЗОБНОВЛЕНИЯ СЕССИИ ==================
    def _handle_session_start(self, topic_id: int, topic_name: str):
        """Единая логика: проверяет наличие незавершённой сессии и предлагает выбор"""
        has_session, session_id, status, existing_topic_id = self.session_controller.has_active_or_paused_session(
            topic_id)

        if has_session:
            reply = SilentMessageBox.question(
                self,
                "Незавершённая сессия",
                f"У вас есть {self._get_status_text_for_dialog(status)} сессия для этой темы.\n\n"
                "• Нажмите «Да» — чтобы завершить её и начать новую\n"
                "• Нажмите «Нет» — чтобы продолжить существующую сессию",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.session_controller.end_session(session_id)
                self.focus_active_view.start_session(topic_id, topic_name)
            else:
                self.focus_active_view.resume_existing_session(session_id, topic_id, topic_name)
        else:
            self.focus_active_view.start_session(topic_id, topic_name)

        self.stack.setCurrentWidget(self.focus_active_view)

    def on_session_ended(self, session_id: int):
        print(f"[DEBUG] on_session_ended: session_id={session_id}")
        self.stack.setCurrentWidget(self.focus_setup_view)
        self.focus_setup_view.refresh()  # обновляем список тем и проверяем активные сессии
        self.tree_widget.load_topics()
        self.refresh_global_cards()

    def show_ping_dialog(self):
        from widgets.ping_dialog import PingDialog

        dialog = PingDialog(self)
        if dialog.exec():
            self.session_controller.user_responded_to_ping()

    # ================== ОБРАБОТКА ВЫБОРА ТЕМЫ ==================
    def on_topic_selected(self, topic_id: int):
        topic_view = TopicView(
            topic_id=topic_id,
            topic_controller=self.topic_controller,
            note_controller=self.note_controller,
            flashcard_controller=self.flashcard_controller,
            task_controller=self.task_controller,
            session_controller=self.session_controller
        )
        topic_view.back_requested.connect(lambda: self.stack.setCurrentIndex(1))
        topic_view.start_session_requested.connect(self._handle_session_start)
        topic_view.resume_existing_session_requested.connect(self.resume_session_from_history)
        topic_view.show_session_analytics.connect(self._show_session_analytics)
        topic_view.cards_updated.connect(self.refresh_global_cards)
        topic_view.topic_updated.connect(self.focus_setup_view.refresh)  # ← обновляем экран фокуса
        topic_view.topic_updated.connect(self.refresh_global_cards)
        self.stack.addWidget(topic_view)
        self.stack.setCurrentWidget(topic_view)

    def _show_session_analytics(self, session_id: int):
        self.stack.setCurrentIndex(7)

    def start_review_session(self, topic_ids: list, include_free: bool, include_qa: bool, skip_reviewed: bool):
        self.review_session_view.start_session(topic_ids, include_free, include_qa, skip_reviewed)
        self.stack.setCurrentWidget(self.review_session_view)

    def refresh_global_cards(self):
        if hasattr(self, 'global_cards_view'):
            self.global_cards_view.refresh()

    def on_topics_changed(self):
        self.focus_setup_view.refresh()  # ← обновляем экран фокуса
        self.refresh_global_cards()
        self.tree_widget.load_topics()

    def resume_session_from_history(self, session_id: int, topic_name: str):
        session = self.session_controller.get_session(session_id)
        if session:
            self.focus_active_view.resume_existing_session(session_id, session.topic_id, topic_name)
            self.stack.setCurrentWidget(self.focus_active_view)

    def _get_status_text_for_dialog(self, status: str) -> str:
        status_map = {
            "active": "активную",
            "paused": "приостановленную",
            "auto_paused": "автоматически приостановленную"
        }
        return status_map.get(status, "незавершённую")

    def _on_focus_clicked(self):
        """Переключение на вкладку фокуса с обновлением"""
        print("[DEBUG] Переключение на вкладку Фокус")
        self.focus_setup_view.refresh()
        self.stack.setCurrentWidget(self.focus_setup_view)