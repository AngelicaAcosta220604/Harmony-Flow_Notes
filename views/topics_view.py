# views/topics_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QGridLayout, QMessageBox, QInputDialog,
    QComboBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from controllers.topic_controller import TopicController


class TopicsView(QWidget):
    """Главная страница со списком всех тем (плитки/список, сортировка, поиск)."""

    topic_selected = Signal(int)  # сигнал для открытия темы

    def __init__(self, topic_controller: TopicController, parent=None):
        super().__init__(parent)
        self.topic_controller = topic_controller
        self.all_topics = []
        self.filtered_topics = []
        self.current_view_mode = "list"  # "list" или "grid"
        self.current_sort_by = "date"  # "date" или "alpha"

        main_layout = QVBoxLayout(self)

        # ========== Поиск ==========
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск по темам...")
        self.search_input.setMinimumHeight(32)
        self.search_input.setStyleSheet("padding: 6px 10px; border: 1px solid #CCC; border-radius: 6px;")
        self.search_input.textChanged.connect(self._filter_topics)
        main_layout.addWidget(self.search_input)

        # ========== Кнопки создания ==========
        buttons_row = QHBoxLayout()
        self.btn_new_folder = QPushButton("📁 Новая папка")
        self.btn_new_topic = QPushButton("📄 Новая тема")

        btn_style = """
            QPushButton {
                padding: 6px 12px;
                background-color: #F0F0F0;
                border: 1px solid #CCC;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #E0E0E0; }
        """
        self.btn_new_folder.setStyleSheet(btn_style)
        self.btn_new_topic.setStyleSheet(btn_style)

        self.btn_new_folder.clicked.connect(self._create_folder)
        self.btn_new_topic.clicked.connect(self._create_topic)

        buttons_row.addWidget(self.btn_new_folder)
        buttons_row.addWidget(self.btn_new_topic)
        buttons_row.addStretch()
        main_layout.addLayout(buttons_row)

        # ========== Панель управления (вид + сортировка) ==========
        control_row = QHBoxLayout()

        self.btn_list_view = QPushButton("📋 Список")
        self.btn_grid_view = QPushButton("📱 Плитки")
        self.btn_list_view.setCheckable(True)
        self.btn_grid_view.setCheckable(True)
        self.btn_list_view.setChecked(True)

        self.btn_list_view.clicked.connect(lambda: self._set_view_mode("list"))
        self.btn_grid_view.clicked.connect(lambda: self._set_view_mode("grid"))

        control_row.addWidget(self.btn_list_view)
        control_row.addWidget(self.btn_grid_view)
        control_row.addSpacing(20)

        sort_label = QLabel("Сортировать:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("📅 По дате создания")
        self.sort_combo.addItem("🔤 По алфавиту")
        self.sort_combo.currentIndexChanged.connect(self._apply_sorting)

        control_row.addWidget(sort_label)
        control_row.addWidget(self.sort_combo)
        control_row.addStretch()

        main_layout.addLayout(control_row)

        # ========== Контейнер для тем (с прокруткой) ==========
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)

        # Загружаем темы
        self._load_topics()

    # ==================== ЗАГРУЗКА ====================
    def _load_topics(self):
        self.all_topics = self.topic_controller.get_all_topics()
        self.filtered_topics = self.all_topics.copy()
        self._apply_sorting()

    # ==================== ОТОБРАЖЕНИЕ ====================
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _display_topics(self, topics):
        # Очищаем контейнер
        self._clear_layout(self.content_layout)

        if not topics:
            empty_label = QLabel("Нет тем. Создайте первую тему!")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: gray; padding: 40px;")
            self.content_layout.addWidget(empty_label)
            return

        if self.current_view_mode == "list":
            for topic in topics:
                card = self._create_topic_card_list(topic)
                self.content_layout.addWidget(card)
        else:
            grid = QGridLayout()
            grid.setSpacing(15)
            grid.setContentsMargins(0, 0, 0, 0)
            row, col = 0, 0
            for topic in topics:
                card = self._create_topic_card_grid(topic)
                grid.addWidget(card, row, col)
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
            self.content_layout.addLayout(grid)

    def _create_topic_card_list(self, topic):
        card = QFrame()
        card.setFrameShape(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                border: 1px solid #DDD;
                border-radius: 6px;
                padding: 10px;
                margin: 2px;
                background-color: white;
            }
            QFrame:hover {
                background-color: #F9F9F9;
                border-color: #AAA;
            }
        """)
        card.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(card)

        icon = "📁" if topic.type == "folder" else "📄"
        title_label = QLabel(f"{icon} {topic.name}")
        title_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(title_label)

        if topic.created_at:
            date_label = QLabel(f"📅 Создано: {topic.created_at[:16]}")
            date_label.setStyleSheet("color: gray; font-size: 11px;")
            layout.addWidget(date_label)

        card.mousePressEvent = lambda e, tid=topic.id: self.topic_selected.emit(tid)
        return card

    def _create_topic_card_grid(self, topic):
        card = QFrame()
        card.setFrameShape(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                border: 1px solid #DDD;
                border-radius: 8px;
                padding: 15px;
                background-color: white;
                min-height: 100px;
            }
            QFrame:hover {
                background-color: #F9F9F9;
                border-color: #AAA;
            }
        """)
        card.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(card)

        icon = "📁" if topic.type == "folder" else "📄"
        title_label = QLabel(f"{icon} {topic.name}")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        if topic.created_at:
            date_label = QLabel(f"📅 {topic.created_at[:16]}")
            date_label.setStyleSheet("color: gray; font-size: 11px;")
            layout.addWidget(date_label)

        layout.addStretch()

        card.mousePressEvent = lambda e, tid=topic.id: self.topic_selected.emit(tid)
        return card

    # ==================== СОРТИРОВКА И ФИЛЬТРАЦИЯ ====================
    def _filter_topics(self, text: str):
        if not text.strip():
            self.filtered_topics = self.all_topics.copy()
        else:
            text_lower = text.lower()
            self.filtered_topics = [t for t in self.all_topics if text_lower in t.name.lower()]
        self._apply_sorting()

    def _apply_sorting(self):
        if not hasattr(self, 'filtered_topics'):
            return
        if self.sort_combo.currentIndex() == 0:  # по дате
            self.filtered_topics.sort(key=lambda x: x.created_at or "", reverse=True)
        else:  # по алфавиту
            self.filtered_topics.sort(key=lambda x: x.name.lower())
        self._display_topics(self.filtered_topics)

    def _set_view_mode(self, mode: str):
        self.current_view_mode = mode
        self.btn_list_view.setChecked(mode == "list")
        self.btn_grid_view.setChecked(mode == "grid")
        self._display_topics(self.filtered_topics)

    # ==================== СОЗДАНИЕ ====================
    def _create_folder(self):
        name, ok = QInputDialog.getText(self, "Новая папка", "Введите название папки:")
        if ok and name.strip():
            self.topic_controller.add_topic(name.strip(), parent_id=None, type="folder")
            self._load_topics()

    def _create_topic(self):
        name, ok = QInputDialog.getText(self, "Новая тема", "Введите название темы:")
        if ok and name.strip():
            self.topic_controller.add_topic(name.strip(), parent_id=None, type="topic")
            self._load_topics()

    def refresh(self):
        """Обновляет список тем (вызывается после изменений)."""
        self._load_topics()
