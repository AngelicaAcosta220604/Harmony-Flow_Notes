from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton
)
from PySide6.QtCore import Qt

# Controllers
from controllers.topic_controller import TopicController
from controllers.note_controller import NoteController
from controllers.task_controller import TaskController
from controllers.flashcard_controller import FlashcardController
from controllers.analytics_controller import AnalyticsController
from controllers.calendar_controller import CalendarController
from controllers.session_controller import SessionController
from controllers.settings_controller import SettingsController
from controllers.search_controller import SearchController

# Views
from views.dashboard_view import DashboardView
from views.topics_view import TopicsView
from views.topic_view import TopicView
from views.note_editor_view import NoteEditorView
from views.flashcards_view import FlashcardsView
from views.tasks_view import TasksView
from views.analytics_view import AnalyticsView
from views.calendar_view import CalendarView
from views.focus_setup_view import FocusSetupView
from views.focus_active_view import FocusActiveView
from views.settings_view import SettingsView
from views.search_view import SearchView
from views.onboarding_wizard import OnboardingWizard


class MainWindow(QMainWindow):
    """
    Полный прототип главного окна Harmony&Flow
    с интеграцией всех контроллеров.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Harmony&Flow")
        self.resize(1280, 800)

        # ---------------------------------------------------------
        # Создание контроллеров
        # ---------------------------------------------------------
        self.topic_controller = TopicController()
        self.note_controller = NoteController()
        self.task_controller = TaskController()
        self.flashcard_controller = FlashcardController()
        self.analytics_controller = AnalyticsController()
        self.calendar_controller = CalendarController()
        self.session_controller = SessionController()
        self.settings_controller = SettingsController()
        self.search_controller = SearchController()

        # ---------------------------------------------------------
        # Центральный контейнер
        # ---------------------------------------------------------
        central = QWidget()
        self.setCentralWidget(central)

        self.main_layout = QHBoxLayout(central)

        # ---------------------------------------------------------
        # Левый сайдбар
        # ---------------------------------------------------------
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar)

        self.btn_dashboard = QPushButton("🏠 Главная")
        self.btn_topics = QPushButton("📚 Темы")
        self.btn_focus = QPushButton("⏱ Фокус")
        self.btn_tasks = QPushButton("✅ Задачи")
        self.btn_analytics = QPushButton("📊 Аналитика")
        self.btn_calendar = QPushButton("📅 Календарь")
        self.btn_search = QPushButton("🔍 Поиск")
        self.btn_settings = QPushButton("⚙ Настройки")

        for btn in [
            self.btn_dashboard, self.btn_topics, self.btn_focus,
            self.btn_tasks, self.btn_analytics, self.btn_calendar,
            self.btn_search, self.btn_settings
        ]:
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.PointingHandCursor)
            self.sidebar_layout.addWidget(btn)

        self.sidebar_layout.addStretch()
        self.main_layout.addWidget(self.sidebar, 1)

        # ---------------------------------------------------------
        # Контейнер для экранов
        # ---------------------------------------------------------
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.main_layout.addWidget(self.container, 5)

        # ---------------------------------------------------------
        # Инициализация views с контроллерами
        # ---------------------------------------------------------
        self.views = {
            "dashboard": DashboardView(self.analytics_controller, self.session_controller),
            "topics": TopicsView(self.topic_controller),
            "topic": TopicView(self.topic_controller, self.note_controller, self.flashcard_controller),
            "note_editor": NoteEditorView(self.note_controller, self.flashcard_controller),
            "flashcards": FlashcardsView(self.flashcard_controller),
            "tasks": TasksView(self.task_controller, self.topic_controller),
            "analytics": AnalyticsView(self.analytics_controller),
            "calendar": CalendarView(self.calendar_controller, self.task_controller),
            "focus_setup": FocusSetupView(self.session_controller, self.settings_controller),
            "focus_active": FocusActiveView(self.session_controller, self.note_controller),
            "settings": SettingsView(self.settings_controller),
            "search": SearchView(self.search_controller),
            "onboarding": OnboardingWizard(self.settings_controller),
        }

        # ---------------------------------------------------------
        # Подключение кнопок сайдбара
        # ---------------------------------------------------------
        self.btn_dashboard.clicked.connect(lambda: self.open_view("dashboard"))
        self.btn_topics.clicked.connect(lambda: self.open_view("topics"))
        self.btn_focus.clicked.connect(lambda: self.open_view("focus_setup"))
        self.btn_tasks.clicked.connect(lambda: self.open_view("tasks"))
        self.btn_analytics.clicked.connect(lambda: self.open_view("analytics"))
        self.btn_calendar.clicked.connect(lambda: self.open_view("calendar"))
        self.btn_search.clicked.connect(lambda: self.open_view("search"))
        self.btn_settings.clicked.connect(lambda: self.open_view("settings"))

        # ---------------------------------------------------------
        # Открываем главный экран
        # ---------------------------------------------------------
        self.open_view("dashboard")

    # ---------------------------------------------------------
    # Метод переключения экранов
    # ---------------------------------------------------------
    def open_view(self, name: str):
        """Переключает текущий экран."""

        # Удаляем старый виджет
        for i in reversed(range(self.container_layout.count())):
            widget = self.container_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Добавляем новый
        view = self.views[name]
        self.container_layout.addWidget(view)

        # Скрываем сайдбар в активной фокус-сессии
        if name == "focus_active":
            self.sidebar.hide()
        else:
            self.sidebar.show()

        # Обновляем экран (если есть метод refresh)
        if hasattr(view, "refresh"):
            view.refresh()

    # ---------------------------------------------------------
    # Метод запуска активной сессии
    # ---------------------------------------------------------
    def start_focus_session(self):
        """Переход в активную фокус-сессию."""
        self.open_view("focus_active")
