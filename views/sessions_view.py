# views/sessions_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QMessageBox,
)
from widgets.silent_dialog import SilentMessageBox
from PySide6.QtCore import Qt, Signal
from datetime import datetime

from services import TimeService
from widgets.quick_notes_viewer import QuickNotesViewer


class SessionsView(QWidget):
    """Виджет для отображения истории сессий темы."""

    start_session_requested = Signal(int, str)
    resume_session_requested = Signal(int, str)  # session_id, topic_name

    def __init__(self, session_controller, topic_id: int, topic_name: str, parent=None):
        super().__init__(parent)
        self.session_controller = session_controller
        self.topic_id = topic_id
        self.topic_name = topic_name

        self.current_sessions = []

        self.setup_ui()
        self.load_sessions()

    def setup_ui(self):
        """Настройка интерфейса."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(10, 10, 10, 10)

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

        # Основной скролл-область для списка сессий
        self.main_scroll = QScrollArea()
        self.main_scroll.setWidgetResizable(True)
        self.main_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #F0F0F0;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #CCC;
                border-radius: 4px;
                min-height: 20px;
            }
        """)

        self.sessions_container = QWidget()
        self.sessions_layout = QVBoxLayout(self.sessions_container)
        self.sessions_layout.setAlignment(Qt.AlignTop)
        self.sessions_layout.setSpacing(10)
        self.sessions_layout.setContentsMargins(10, 5, 10, 5)

        self.main_scroll.setWidget(self.sessions_container)
        layout.addWidget(self.main_scroll)

    def load_sessions(self):
        self.current_sessions = self.session_controller.get_sessions_by_topic(self.topic_id)
        self.display_sessions()

    def display_sessions(self):
        # Очищаем контейнер
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
        card_frame.setSizePolicy(card_frame.sizePolicy().horizontalPolicy(), card_frame.sizePolicy().verticalPolicy())
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
        layout.setSpacing(5)

        # Верхняя строка
        header_layout = QHBoxLayout()

        date_label = QLabel(f"⏱ {TimeService.format_display(session.start_time)}")
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
        info_layout.addSpacing(0)

        time_text = self._format_time_range(session.start_time, session.end_time)
        if time_text:
            time_label = QLabel(f"📅 {time_text}")
            time_label.setStyleSheet("color: #888; font-size: 11px;")
            info_layout.addWidget(time_label)

        info_layout.addStretch()

        # Кнопка "Быстрые записи"
        quick_notes_btn = QPushButton("📝 Быстрые записи")
        quick_notes_btn.setFixedSize(110, 26)
        quick_notes_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        quick_notes_btn.setToolTip("Просмотреть быстрые записи этой сессии")
        quick_notes_btn.clicked.connect(lambda checked, sid=session.id: self._show_quick_notes(sid))
        info_layout.addWidget(quick_notes_btn)

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
        delete_btn.setToolTip("Удалить всю сессию")
        delete_btn.clicked.connect(lambda checked, sid=session.id: self._delete_session(sid))
        info_layout.addWidget(delete_btn)

        layout.addLayout(info_layout)

        # Обработчик клика по всей карточке (кроме кнопок)
        card_frame.mousePressEvent = lambda event, sid=session.id, stat=session.status: self._on_card_clicked(event,
                                                                                                              sid, stat)

        return card_frame

    def _on_card_clicked(self, event, session_id: int, status: str):
        """Обработчик клика по карточке сессии"""
        # Получаем виджет, на котором произошёл клик
        child = self.childAt(event.pos())

        # Если клик был по кнопке или её дочернему элементу — не обрабатываем
        if child:
            # Проверяем, является ли виджет кнопкой или имеет кнопку в родителях
            while child:
                if isinstance(child, QPushButton):
                    return
                child = child.parent()

        # Если сессия не завершена (активна или на паузе)
        if status in ("active", "paused", "auto_paused"):
            reply = SilentMessageBox.question(
                self,
                "Возобновить сессию?",
                f"Эта сессия {self._get_status_text(status)}. Хотите её продолжить?"
            )
            if reply == QMessageBox.Yes:
                self.resume_session_requested.emit(session_id, self.topic_name)
        else:
            # Для завершённых сессий можно показать аналитику
            session = self._get_session_by_id(session_id)
            if session:
                SilentMessageBox.information(
                    self,
                    "Завершённая сессия",
                    f"Сессия завершена {TimeService.format_display(session.start_time)}.\n"
                    f"Длительность: {session.duration_minutes} минут."
                )

    def _get_session_by_id(self, session_id: int):
        """Возвращает сессию по ID"""
        for session in self.current_sessions:
            if session.id == session_id:
                return session
        return None

    def _show_quick_notes(self, session_id: int):
        """Открывает окно с быстрыми записями сессии"""
        dialog = QuickNotesViewer(self.session_controller, session_id, self)
        dialog.exec()

    def _format_time_range(self, start_str, end_str):
        if not start_str:
            return ""
        try:
            start_time = TimeService.format_display(start_str).split()[-1]
            if end_str:
                end_time = TimeService.format_display(end_str).split()[-1]
                return f"{start_time} - {end_time}"
            else:
                return f"Начата в {start_time}"
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
        reply = SilentMessageBox.question(self, "Удаление сессии",
                                          "Вы уверены, что хотите удалить эту сессию?\n"
                                          "Все данные будут удалены безвозвратно."
                                          )
        if reply == QMessageBox.Yes:
            self.session_controller.delete_session(session_id)
            self.load_sessions()
            SilentMessageBox.information(self, "Готово", "Сессия удалена")

    def _delete_quick_note(self, note_id: int, session_id: int):
        """Удаляет быструю запись (вызывается из диалога)"""
        reply = SilentMessageBox.question(
            self, "Удаление записи",
            "Вы уверены, что хотите удалить эту быструю запись?"
        )
        if reply == QMessageBox.Yes:
            from database.db_manager import db
            db.execute("DELETE FROM quick_notes WHERE id = ?", (note_id,))
            self.load_sessions()

    def _on_start_session(self):
        self.start_session_requested.emit(self.topic_id, self.topic_name)

    def refresh(self):
        self.load_sessions()