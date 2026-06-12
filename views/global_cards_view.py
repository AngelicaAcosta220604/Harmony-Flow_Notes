# views/global_cards_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QScrollArea, QMessageBox, QCheckBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from widgets.topic_tree_selector import TopicTreeSelector
from controllers.review_controller import ReviewController


class GlobalCardsView(QWidget):
    """Главная страница карточек: выбор тем, статистика, запуск повторения"""

    start_review_requested = Signal(list, bool, bool)  # topic_ids, include_free, include_qa

    def __init__(self, flashcard_controller, topic_controller, parent=None):
        super().__init__(parent)
        self.flashcard_controller = flashcard_controller
        self.topic_controller = topic_controller
        self.review_controller = ReviewController()

        self.setup_ui()
        self.load_stats()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # ========== Заголовок ==========
        title = QLabel("🃏 Карточки")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # ========== Верхняя панель: статистика + быстрый старт ==========
        top_panel = QHBoxLayout()
        top_panel.setSpacing(20)

        # Статистика
        self.stats_frame = QFrame()
        self.stats_frame.setFrameShape(QFrame.Box)
        self.stats_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #DDD;
                border-radius: 8px;
                background-color: #F8F9FA;
            }
        """)
        stats_layout = QVBoxLayout(self.stats_frame)

        self.total_label = QLabel("📊 Всего карточек: 0")
        self.reviewed_label = QLabel("✅ Выучено: 0")
        self.learning_label = QLabel("📖 В процессе: 0")
        self.new_label = QLabel("🆕 Новых: 0")

        for label in [self.total_label, self.reviewed_label, self.learning_label, self.new_label]:
            label.setStyleSheet("font-size: 13px; padding: 2px 0;")
            stats_layout.addWidget(label)

        top_panel.addWidget(self.stats_frame, 1)

        # Блок быстрого старта
        quick_start_frame = QFrame()
        quick_start_frame.setFrameShape(QFrame.Box)
        quick_start_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #DDD;
                border-radius: 8px;
                background-color: #F8F9FA;
            }
        """)
        quick_layout = QVBoxLayout(quick_start_frame)

        quick_layout.addWidget(QLabel("🚀 Быстрый старт"))

        # Выбор типа карточек
        type_layout = QHBoxLayout()
        self.include_free_cb = QCheckBox("📝 Свободные")
        self.include_qa_cb = QCheckBox("❓ Вопрос-Ответ")
        self.include_free_cb.setChecked(True)
        self.include_qa_cb.setChecked(True)
        type_layout.addWidget(self.include_free_cb)
        type_layout.addWidget(self.include_qa_cb)
        quick_layout.addLayout(type_layout)

        self.start_btn = QPushButton("▶ Начать повторение")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                margin-top: 10px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.start_btn.clicked.connect(self.start_review)
        quick_layout.addWidget(self.start_btn)

        top_panel.addWidget(quick_start_frame, 1)
        layout.addLayout(top_panel)

        # ========== Выбор тем (дерево с чекбоксами) ==========
        group_box = QGroupBox("📚 Выберите темы для повторения")
        group_box.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #DDD;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        group_layout = QVBoxLayout(group_box)

        self.tree_selector = TopicTreeSelector(self.topic_controller)
        group_layout.addWidget(self.tree_selector)

        # Кнопки выбора
        select_buttons_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("Выбрать все")
        self.clear_all_btn = QPushButton("Снять все")
        self.select_all_btn.clicked.connect(self.tree_selector.select_all)
        self.clear_all_btn.clicked.connect(self.tree_selector.clear_all)

        select_buttons_layout.addWidget(self.select_all_btn)
        select_buttons_layout.addWidget(self.clear_all_btn)
        select_buttons_layout.addStretch()
        group_layout.addLayout(select_buttons_layout)

        layout.addWidget(group_box, 1)

        # ========== Кнопка обновления статистики ==========
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()
        self.refresh_btn = QPushButton("🔄 Обновить статистику")
        self.refresh_btn.clicked.connect(self.load_stats)
        refresh_layout.addWidget(self.refresh_btn)
        layout.addLayout(refresh_layout)

    def load_stats(self):
        """Загружает и отображает общую статистику"""
        stats = self.flashcard_controller.get_review_stats()
        self.total_label.setText(f"📊 Всего карточек: {stats['total']}")
        self.reviewed_label.setText(f"✅ Выучено: {stats['reviewed']}")
        self.learning_label.setText(f"📖 В процессе: {stats['learning']}")
        self.new_label.setText(f"🆕 Новых: {stats['new_cards']}")

    def start_review(self):
        """Запускает сессию повторения"""
        selected_topics = self.tree_selector.get_selected_topic_ids()

        if not selected_topics:
            QMessageBox.warning(self, "Нет тем", "Выберите хотя бы одну тему для повторения!")
            return

        include_free = self.include_free_cb.isChecked()
        include_qa = self.include_qa_cb.isChecked()

        if not include_free and not include_qa:
            QMessageBox.warning(self, "Нет типов", "Выберите хотя бы один тип карточек!")
            return

        # Проверяем, есть ли карточки для повторения
        cards = self.flashcard_controller.get_cards_for_review(
            selected_topics, include_free, include_qa
        )

        if not cards:
            QMessageBox.information(
                self, "Нет карточек",
                "В выбранных темах нет активных карточек для повторения!\n\n"
                "Создайте карточки через раздел 'Темы' → выберите тему → 'Карточки'."
            )
            return

        # Отправляем сигнал в MainWindow для переключения на окно повторения
        self.start_review_requested.emit(selected_topics, include_free, include_qa)

    def refresh(self):
        """Обновляет всё (вызывается при переключении на вкладку)"""
        self.load_stats()
        self.tree_selector.load_topics()