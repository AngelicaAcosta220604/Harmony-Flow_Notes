# views/focus_setup_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal


class FocusSetupView(QWidget):
    """
    Экран настройки фокус-сессии.
    """

    start_session_requested = Signal(int, str)
    resume_session_requested = Signal(int, str)

    def __init__(self, session_controller, settings_controller, topic_controller, parent=None):
        super().__init__(parent)
        self.session_controller = session_controller
        self.settings_controller = settings_controller
        self.topic_controller = topic_controller

        self.resume_session_id = None
        self.resume_topic_id = None
        self.resume_topic_name = None

        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        # Главный layout с центрированием
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # Центральный контейнер
        center_container = QWidget()
        center_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        center_layout = QVBoxLayout(center_container)
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setSpacing(25)

        # Заголовок
        title = QLabel("🎯 Фокус-сессия")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2C3E50;
            margin-bottom: 10px;
        """)
        center_layout.addWidget(title)

        # Подзаголовок
        subtitle = QLabel("Сосредоточься на одной теме")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #7F8C8D;
            margin-bottom: 20px;
        """)
        center_layout.addWidget(subtitle)

        # Карточка выбора темы
        theme_card = QFrame()
        theme_card.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #E0E0E0;
                border-radius: 16px;
                padding: 20px;
            }
        """)
        theme_layout = QVBoxLayout(theme_card)
        theme_layout.setSpacing(15)

        theme_label = QLabel("📚 Выберите тему для фокуса:")
        theme_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #2C3E50;")
        theme_layout.addWidget(theme_label)

        self.topic_combo = QComboBox()
        self.topic_combo.setStyleSheet("""
            QComboBox {
                padding: 10px 12px;
                border: 1px solid #CCC;
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
                min-height: 20px;
            }
            QComboBox:hover { border-color: #999; }
            QComboBox::drop-down { border: none; }
        """)
        self.topic_combo.currentIndexChanged.connect(self._on_topic_changed)
        theme_layout.addWidget(self.topic_combo)

        center_layout.addWidget(theme_card)

        # Кнопка "Начать сессию"
        self.start_btn = QPushButton("▶ Начать сессию")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 24px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3d8b40; }
        """)
        self.start_btn.clicked.connect(self._on_start_clicked)
        center_layout.addWidget(self.start_btn)

        # Блок с активной сессией
        self.active_session_frame = QFrame()
        self.active_session_frame.setStyleSheet("""
            QFrame {
                background-color: #FFF8E1;
                border: 1px solid #FFE082;
                border-radius: 16px;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        self.active_session_frame.hide()

        active_layout = QVBoxLayout(self.active_session_frame)
        active_layout.setSpacing(10)

        active_header = QHBoxLayout()
        active_icon = QLabel("⏵")
        active_icon.setStyleSheet("font-size: 20px; color: #FF9800;")
        active_header.addWidget(active_icon)

        active_title = QLabel("У вас есть незавершённая сессия")
        active_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #E65100;")
        active_header.addWidget(active_title)
        active_header.addStretch()
        active_layout.addLayout(active_header)

        self.session_info_label = QLabel()
        self.session_info_label.setStyleSheet("font-size: 13px; color: #555;")
        self.session_info_label.setWordWrap(True)
        active_layout.addWidget(self.session_info_label)

        self.resume_btn = QPushButton("⏵ Продолжить сессию")
        self.resume_btn.setMinimumHeight(40)
        self.resume_btn.setCursor(Qt.PointingHandCursor)
        self.resume_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #F57C00; }
        """)
        self.resume_btn.clicked.connect(self._on_resume_clicked)
        active_layout.addWidget(self.resume_btn)

        center_layout.addWidget(self.active_session_frame)
        main_layout.addWidget(center_container)

    def refresh_topics(self):
        """Обновляет список тем в комбобоксе"""
        print("[DEBUG] FocusSetupView.refresh_topics()")
        self.topic_combo.blockSignals(True)
        current_topic_id = self.topic_combo.currentData()
        self.topic_combo.clear()

        topics = self.topic_controller.get_all_topics()
        for topic in topics:
            if topic.type == "topic":
                self.topic_combo.addItem(topic.name, topic.id)

        if current_topic_id:
            index = self.topic_combo.findData(current_topic_id)
            if index >= 0:
                self.topic_combo.setCurrentIndex(index)

        self.topic_combo.blockSignals(False)
        self._on_topic_changed()

    def _on_topic_changed(self):
        """Проверяет активную сессию для выбранной темы"""
        topic_id = self.topic_combo.currentData()
        print(f"[DEBUG] _on_topic_changed: topic_id={topic_id}")

        if not topic_id:
            self.active_session_frame.hide()
            return

        has_session, session_id, status, existing_topic_id = self.session_controller.has_active_or_paused_session(
            topic_id)
        print(
            f"[DEBUG] has_session={has_session}, session_id={session_id}, status={status}, existing_topic_id={existing_topic_id}")

        if has_session and session_id and existing_topic_id == topic_id:
            topic = self.topic_controller.get_topic(topic_id)
            topic_name = topic.name if topic else "неизвестная тема"

            if status == "active":
                status_text = "активна"
                btn_text = "⏵ Продолжить активную сессию"
            elif status == "paused":
                status_text = "на паузе"
                btn_text = "⏵ Продолжить сессию (была на паузе)"
            else:
                status_text = "приостановлена"
                btn_text = "⏵ Продолжить сессию"

            session = self.session_controller.get_session(session_id)
            if session:
                total_seconds = session.total_active_seconds
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                time_str = f"{hours} ч {minutes} мин" if hours > 0 else f"{minutes} мин"
            else:
                time_str = "несколько минут"

            self.session_info_label.setText(
                f"📌 Тема: {topic_name}\n"
                f"📊 Статус: {status_text}\n"
                f"⏱ Накопленное время: {time_str}"
            )
            self.resume_btn.setText(btn_text)
            self.resume_session_id = session_id
            self.resume_topic_id = topic_id
            self.resume_topic_name = topic_name
            self.active_session_frame.show()
        else:
            self.active_session_frame.hide()
            self.resume_session_id = None

    def refresh(self):
        """Обновляет данные при переключении на вкладку"""
        print("[DEBUG] FocusSetupView.refresh() вызван")
        self.refresh_topics()

    def _on_start_clicked(self):
        current_index = self.topic_combo.currentIndex()
        if current_index < 0:
            from widgets.silent_dialog import SilentMessageBox
            SilentMessageBox.warning(self, "Ошибка", "Нет доступных тем для сессии")
            return

        topic_id = self.topic_combo.currentData()
        topic_name = self.topic_combo.currentText()
        self.start_session_requested.emit(topic_id, topic_name)

    def _on_resume_clicked(self):
        if hasattr(self, 'resume_session_id') and self.resume_session_id:
            self.resume_session_requested.emit(self.resume_session_id, self.resume_topic_name)