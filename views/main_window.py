# views/main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame
)
from PySide6.QtCore import Qt
from widgets.tree_widget import TreeWidget
from controllers.topic_controller import TopicController
from controllers.note_controller import NoteController
from controllers.flashcard_controller import FlashcardController
from controllers.task_controller import TaskController
from controllers.session_controller import SessionController
from views.topic_view import TopicView


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

        # Страница 1: Главная
        page_home = QLabel("🏠 Главная страница\n\nДобро пожаловать в HFlow!")
        page_home.setAlignment(Qt.AlignCenter)
        page_home.setStyleSheet("font-size: 20px;")

        # Страница 2: Темы (с деревом, которому передаём контроллер)
        self.page_topics = TreeWidget(topic_controller=self.topic_controller)

        # ПОДПИСКА НА СИГНАЛ ВЫБОРА ТЕМЫ
        self.page_topics.topic_selected.connect(self.on_topic_selected)

        # Страница 3: Фокус
        page_focus = QLabel("⏱ Фокус-сессия\n\nЗдесь будет таймер и ползунки")
        page_focus.setAlignment(Qt.AlignCenter)

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
        self.stack.addWidget(page_home)           # индекс 0
        self.stack.addWidget(self.page_topics)    # индекс 1
        self.stack.addWidget(page_focus)          # индекс 2
        self.stack.addWidget(page_tasks)          # индекс 3
        self.stack.addWidget(page_analytics)      # индекс 4
        self.stack.addWidget(page_settings)       # индекс 5

        # ================== Собираем всё ==================
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, 1)

        # ================== Подключаем кнопки ==================
        btn_home.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_topics.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_focus.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        btn_tasks.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        btn_analytics.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        btn_settings.clicked.connect(lambda: self.stack.setCurrentIndex(5))

        # Загружаем реальные темы из БД при старте
        self.page_topics.load_topics()

    # ================== МЕТОД ВЫБОРА ТЕМЫ (ПРАВИЛЬНОЕ МЕСТО) ==================
    def on_topic_selected(self, topic_id: int):
        """Обработчик клика по теме в дереве"""
        topic_view = TopicView(
            topic_id=topic_id,
            topic_controller=self.topic_controller,
            note_controller=self.note_controller,
            flashcard_controller=self.flashcard_controller,
            task_controller=self.task_controller,
            session_controller=self.session_controller
        )
        # Подключаем сигнал возврата к переключению на страницу с деревом тем (индекс 1)
        topic_view.back_requested.connect(lambda: self.stack.setCurrentIndex(1))
        self.stack.addWidget(topic_view)
        self.stack.setCurrentWidget(topic_view)