# views/sessions_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from datetime import datetime


class SessionsView(QWidget):
    """Виджет для отображения истории сессий темы."""

    start_session_requested = Signal(int, str)  # topic_id, topic_name

    def __init__(self, session_controller, topic_id: int, topic_name: str, parent=None):
        super().__init__(parent)
        self.session_controller = session_controller
        self.topic_id = topic_id
        self.topic_name = topic_name
        self.expanded_items = set()

        self.current_sessions = []

        self.setup_ui()
        self.load_sessions()

    def setup_ui(self):
        """Настройка интерфейса."""
        layout = QVBoxLayout(self)

        top_bar = QHBoxLayout()

        self.start_btn = QPushButton("▶ Начать сессию")
        self.start_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.start_btn.clicked.connect(self._on_start_session)
        top_bar.addWidget(self.start_btn)

        top_bar.addStretch()

        self.sessions_count_label = QLabel()
        self.sessions_count_label.setStyleSheet("color: gray; font-size: 12px;")
        top_bar.addWidget(self.sessions_count_label)

        layout.addLayout(top_bar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.sessions_container = QWidget()
        self.sessions_layout = QVBoxLayout(self.sessions_container)
        self.sessions_layout.setAlignment(Qt.AlignTop)
        self.sessions_layout.setSpacing(10)

        self.scroll_area.setWidget(self.sessions_container)
        layout.addWidget(self.scroll_area)

    def load_sessions(self):
        self.current_sessions = self.session_controller.get_sessions_by_topic(self.topic_id)
        self.display_sessions()

    def display_sessions(self):
        while self.sessions_layout.count():
            item = self.sessions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        count = len(self.current_sessions)
        if count == 0:
            self.sessions_count_label.setText("Нет проведённых сессий")
        else:
            total_minutes = sum(s.duration_minutes or 0 for s in self.current_sessions)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            self.sessions_count_label.setText(f"📊 {count} сессий · {hours}ч {minutes}мин")

        if not self.current_sessions:
            empty_label = QLabel("Нет проведённых сессий.\nНажмите «Начать сессию», чтобы провести первую!")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: gray; padding: 40px;")
            self.sessions_layout.addWidget(empty_label)
            return

        for session in self.current_sessions:
            session_widget = self._create_session_card(session)
            self.sessions_layout.addWidget(session_widget)

    def _create_session_card(self, session):
        card_frame = QFrame()
        card_frame.setFrameShape(QFrame.Box)
        card_frame.setProperty("session_id", session.id)
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
            }
        """)

        layout = QVBoxLayout(card_frame)

        # Верхняя строка
        header_layout = QHBoxLayout()

        expand_btn = QPushButton("▶")
        expand_btn.setFixedSize(24, 24)
        expand_btn.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 12px;
                background-color: transparent;
            }
            QPushButton:hover {
                color: #51b2c1;
            }
        """)
        is_expanded = session.id in self.expanded_items
        expand_btn.setText("▼" if is_expanded else "▶")
        expand_btn.clicked.connect(lambda checked, sid=session.id, btn=expand_btn: self._toggle_expand(sid, btn))
        header_layout.addWidget(expand_btn)

        date_label = QLabel("⏱ " + self._format_datetime(session.start_time))
        date_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        header_layout.addWidget(date_label)

        header_layout.addStretch()

        if session.duration_minutes:
            hours = session.duration_minutes // 60
            minutes = session.duration_minutes % 60
            if hours > 0:
                duration_text = f"🕐 {hours}ч {minutes}мин"
            else:
                duration_text = f"🕐 {minutes}мин"
            duration_label = QLabel(duration_text)
            duration_label.setStyleSheet("color: #555; font-size: 12px;")
            header_layout.addWidget(duration_label)

        status_text = self._get_status_text(session.status)
        status_label = QLabel(status_text)
        if session.status == "completed":
            status_label.setStyleSheet("color: #4CAF50; font-size: 11px;")
        elif session.status in ("paused", "auto_paused"):
            status_label.setStyleSheet("color: #FF9800; font-size: 11px;")
        else:
            status_label.setStyleSheet("color: #666; font-size: 11px;")
        header_layout.addWidget(status_label)

        layout.addLayout(header_layout)

        # Вторая строка
        info_layout = QHBoxLayout()
        info_layout.addSpacing(30)

        time_text = self._format_time_range(session.start_time, session.end_time)
        if time_text:
            time_label = QLabel(f"📅 {time_text}")
            time_label.setStyleSheet("color: #888; font-size: 11px;")
            info_layout.addWidget(time_label)

        info_layout.addStretch()

        # analytics_btn = QPushButton("📊 Аналитика сессии")
        # analytics_btn.setFixedSize(130, 26)
        # analytics_btn.setStyleSheet("""
        #     QPushButton {
        #         background-color: #2196F3;
        #         color: white;
        #         border: none;
        #         border-radius: 4px;
        #         font-size: 11px;
        #     }
        #     QPushButton:hover {
        #         background-color: #0b7dda;
        #     }
        # """)
        # Вызываем сигнал, который будет обработан в TopicView
        # analytics_btn.clicked.connect(lambda checked, sid=session.id: self._on_analytics_clicked(sid))
        # info_layout.addWidget(analytics_btn)

        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.setFixedSize(80, 26)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        delete_btn.clicked.connect(lambda checked, sid=session.id: self._delete_session(sid))
        info_layout.addWidget(delete_btn)

        layout.addLayout(info_layout)

        # Раскрывающаяся часть
        expand_widget = QWidget()
        expand_widget.setVisible(is_expanded)
        expand_layout = QVBoxLayout(expand_widget)
        expand_layout.setContentsMargins(30, 10, 0, 5)

        quick_notes = self.session_controller.get_quick_notes(session.id)

        if quick_notes:
            expand_layout.addWidget(QLabel("📝 Быстрые записи во время сессии:"))
            for note in quick_notes:
                note_frame = self._create_note_widget(note)
                expand_layout.addWidget(note_frame)
        else:
            empty_label = QLabel("Нет быстрых записей во время этой сессии")
            empty_label.setStyleSheet("color: #999; font-size: 11px;")
            expand_layout.addWidget(empty_label)

        layout.addWidget(expand_widget)

        return card_frame

    # def _on_analytics_clicked(self, session_id: int):
    #     """Отправляет сигнал родительскому окну для показа аналитики"""
    #     # Находим родительский TopicView
    #     parent = self.parent()
    #     while parent and not hasattr(parent, 'show_session_analytics_from_session'):
    #         parent = parent.parent()
    #     if parent and hasattr(parent, 'show_session_analytics_from_session'):
    #         parent.show_session_analytics_from_session(session_id)

    def _create_note_widget(self, note):
        note_frame = QFrame()
        note_frame.setStyleSheet("""
            QFrame {
                border: none;
                background-color: #f5f5f5;
                border-radius: 4px;
                padding: 5px;
                margin: 2px 0;
            }
        """)

        layout = QVBoxLayout(note_frame)
        layout.setContentsMargins(8, 5, 8, 5)

        if note.created_at:
            try:
                dt = datetime.fromisoformat(note.created_at)
                date_label = QLabel(f"📌 {dt.strftime('%d.%m.%Y %H:%M')}")
                date_label.setStyleSheet("color: #888; font-size: 10px;")
                layout.addWidget(date_label)
            except:
                pass

        text_label = QLabel(note.content)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("color: #333; font-size: 12px;")
        layout.addWidget(text_label)

        return note_frame

    def _toggle_expand(self, session_id: int, btn):
        if session_id in self.expanded_items:
            self.expanded_items.remove(session_id)
            btn.setText("▶")
        else:
            self.expanded_items.add(session_id)
            btn.setText("▼")
        self.display_sessions()

    def _format_datetime(self, datetime_str):
        if not datetime_str:
            return ""
        try:
            dt = datetime.fromisoformat(datetime_str)
            return dt.strftime("%d.%m.%Y %H:%M")
        except:
            return datetime_str[:16]

    def _format_time_range(self, start_str, end_str):
        if not start_str:
            return ""
        try:
            start = datetime.fromisoformat(start_str)
            if end_str:
                end = datetime.fromisoformat(end_str)
                return f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"
            else:
                return f"Начата в {start.strftime('%H:%M')}"
        except:
            return start_str

    def _get_status_text(self, status):
        status_map = {
            "completed": "✅ Завершена",
            "active": "🟢 Активна",
            "paused": "⏸ На паузе",
            "auto_paused": "⏸ Авто-пауза",
            "auto_completed": "⏹ Авто-завершена"
        }
        return status_map.get(status, "❓ " + status)

    def _delete_session(self, session_id: int):
        reply = QMessageBox.question(
            self, "Удаление сессии",
            "Вы уверены, что хотите удалить эту сессию?\n"
            "Все данные будут удалены безвозвратно.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.session_controller.delete_session(session_id)
            self.load_sessions()
            QMessageBox.information(self, "Готово", "Сессия удалена")

    def _on_start_session(self):
        self.start_session_requested.emit(self.topic_id, self.topic_name)

    def refresh(self):
        self.load_sessions()