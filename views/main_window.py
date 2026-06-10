# views/main_window.py

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from widgets.tree_widget import TreeWidget  # ← ИЗМЕНЕНО: вместо TopicsView
from views.focus_active_view import FocusActiveView
from controllers.topic_controller import TopicController
from controllers.note_controller import NoteController
from controllers.flashcard_controller import FlashcardController
from controllers.task_controller import TaskController
from controllers.session_controller import SessionController
from views.topic_view import TopicView
from utils.ping_manager import PingManager


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
        for btn in [btn_home, btn_topics, btn_focus, btn_tasks, btn_analytics, btn_settings]:
            btn.setStyleSheet(btn_style)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # ================== Правая область (StackedWidget) ==================
        self.stack = QStackedWidget()

        # Страница 0: Главная
        page_home = QLabel("🏠 Главная страница\n\nДобро пожаловать в HFlow!")
        page_home.setAlignment(Qt.AlignCenter)
        page_home.setStyleSheet("font-size: 20px;")

        # Страница 1: Дерево тем (используем TreeWidget)
        self.tree_widget = TreeWidget(topic_controller=self.topic_controller)
        self.tree_widget.topic_selected.connect(self.on_topic_selected)

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

        # Страница 5: Аналитика
        page_analytics = QLabel("📊 Аналитика\n\nГрафики и статистика")
        page_analytics.setAlignment(Qt.AlignCenter)

        # Страница 6: Настройки
        page_settings = QLabel("⚙ Настройки\n\nПараметры приложения")
        page_settings.setAlignment(Qt.AlignCenter)

        # Добавляем страницы
        self.stack.addWidget(page_home)  # индекс 0
        self.stack.addWidget(self.tree_widget)  # индекс 1 - дерево тем
        self.stack.addWidget(self.focus_setup_view)  # индекс 2
        self.stack.addWidget(self.focus_active_view)  # индекс 3
        self.stack.addWidget(page_tasks)  # индекс 4
        self.stack.addWidget(page_analytics)  # индекс 5
        self.stack.addWidget(page_settings)  # индекс 6

        # ================== Собираем всё ==================
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, 1)

        # ================== Подключаем кнопки ==================
        btn_home.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_topics.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_focus.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        btn_tasks.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        btn_analytics.clicked.connect(lambda: self.stack.setCurrentIndex(5))
        btn_settings.clicked.connect(lambda: self.stack.setCurrentIndex(6))

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
            QMessageBox.warning(self, "Ошибка", "Сначала создайте хотя бы одну тему!")
            return

        topic_id = self.session_topic_combo.currentData()
        topic_name = self.session_topic_combo.currentText()

        self.focus_active_view.start_session(topic_id, topic_name)
        self.stack.setCurrentWidget(self.focus_active_view)

    def on_session_ended(self, session_id: int):
        self.stack.setCurrentIndex(2)
        self.refresh_topic_combo()
        # Обновляем дерево тем
        self.tree_widget.load_topics()

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
        self.stack.addWidget(topic_view)
        self.stack.setCurrentWidget(topic_view)