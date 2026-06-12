# views/focus_active_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Signal
from widgets.state_sliders import StateSliders
from widgets.custom_timer import CustomTimer
from widgets.music_widget import MusicWidget
from widgets.quick_note_dialog import QuickNoteDialog
from widgets.ping_dialog import PingDialog


class FocusActiveView(QWidget):
    """Экран активной фокус-сессии"""

    session_ended = Signal(int)
    back_to_topics = Signal()

    def __init__(self, session_controller, note_controller, topic_controller, parent=None):
        super().__init__(parent)
        self.session_controller = session_controller
        self.note_controller = note_controller
        self.topic_controller = topic_controller

        self.current_session_id = None
        self.current_topic_id = None
        self.current_topic_name = ""

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Создаёт интерфейс активной сессии"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # ========== Верхняя панель ==========
        top_bar = QHBoxLayout()

        self.back_button = QPushButton("← Выйти из сессии")
        self.back_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #FF4444;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #CC0000;
            }
        """)
        top_bar.addWidget(self.back_button)

        top_bar.addStretch()

        self.topic_label = QLabel()
        self.topic_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_bar.addWidget(self.topic_label)

        top_bar.addStretch()

        main_layout.addLayout(top_bar)

        # ========== Центр: Таймер ==========
        timer_container = QFrame()
        timer_container.setStyleSheet("""
            QFrame {
                border: 2px solid #DDD;
                border-radius: 15px;
                background-color: #F9F9F9;
            }
        """)
        timer_layout = QVBoxLayout(timer_container)

        self.timer = CustomTimer()
        timer_layout.addWidget(self.timer, alignment=Qt.AlignCenter)

        main_layout.addWidget(timer_container)

        # ========== Нижняя часть ==========
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(30)

        # ----- Левая колонка: Ползунки -----
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                border: 1px solid #DDD;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("📊 Твоё состояние"))

        self.state_sliders = StateSliders()
        left_layout.addWidget(self.state_sliders)

        hint_label = QLabel("💡 Меняй ползунки, когда чувствуешь изменения")
        hint_label.setStyleSheet("color: gray; font-size: 11px;")
        hint_label.setWordWrap(True)
        left_layout.addWidget(hint_label)

        bottom_row.addWidget(left_panel, stretch=2)

        # ----- Правая колонка: Кнопки -----
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                border: 1px solid #DDD;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)

        self.quick_note_btn = QPushButton("✏️ Быстрая запись")
        self.quick_note_btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        right_layout.addWidget(self.quick_note_btn)
        # После кнопки "Быстрая запись", перед "Пауза"
        self.save_state_btn = QPushButton("💾 Сохранить состояние")
        self.save_state_btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #7B1FA2; }
        """)
        self.save_state_btn.clicked.connect(self.log_current_state)
        right_layout.addWidget(self.save_state_btn)
        self.pause_btn = QPushButton("⏸ Пауза")
        self.pause_btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #e68900; }
        """)
        right_layout.addWidget(self.pause_btn)

        self.end_btn = QPushButton("⏹ Завершить")
        self.end_btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #da190b; }
        """)
        right_layout.addWidget(self.end_btn)

        right_layout.addStretch()

        self.music_widget = MusicWidget()
        right_layout.addWidget(self.music_widget)

        bottom_row.addWidget(right_panel, stretch=1)
        main_layout.addLayout(bottom_row)

    def connect_signals(self):
        """Подключает сигналы"""
        self.quick_note_btn.clicked.connect(self.show_quick_note_dialog)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.end_btn.clicked.connect(self.end_session)
        self.back_button.clicked.connect(self.confirm_exit)

    # =========================================================
    # УПРАВЛЕНИЕ СЕССИЕЙ
    # =========================================================

    def start_session(self, topic_id: int, topic_name: str):
        """Запускает новую сессию"""
        self.current_topic_id = topic_id
        self.current_topic_name = topic_name
        self.topic_label.setText(f"📚 {topic_name}")

        self.current_session_id = self.session_controller.start_session(topic_id)
        self.timer.start()

        self.pause_btn.setText("⏸ Пауза")
        self.pause_btn.setEnabled(True)
        self.end_btn.setEnabled(True)

    def toggle_pause(self):
        """Пауза / Возобновление"""
        if not self.timer.running:
            # Возобновляем
            self.timer.resume()
            self.session_controller.resume_session(self.current_session_id)
            self.pause_btn.setText("⏸ Пауза")
            self.pause_btn.setStyleSheet("""
                QPushButton {
                    padding: 12px;
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    border-radius: 8px;
                }
                QPushButton:hover { background-color: #e68900; }
            """)
        else:
            # Ставим на паузу
            self.timer.pause()
            self.session_controller.pause_session(self.current_session_id)
            self.pause_btn.setText("▶ Возобновить")
            self.pause_btn.setStyleSheet("""
                QPushButton {
                    padding: 12px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 8px;
                }
                QPushButton:hover { background-color: #45a049; }
            """)

    def end_session(self):
        """Завершает сессию"""
        self.timer.pause()
        duration_seconds = self.timer.get_seconds()
        duration_minutes = duration_seconds // 60

        self.session_controller.end_session(self.current_session_id, duration=duration_minutes)

        QMessageBox.information(
            self,
            "Сессия завершена",
            f"Сессия по теме '{self.current_topic_name}' завершена!\n\n"
            f"⏱ Длительность: {duration_minutes} минут"
        )

        self.session_ended.emit(self.current_session_id)
        self.current_session_id = None
        self.timer.reset()

    def confirm_exit(self):
        """Подтверждение выхода"""
        reply = QMessageBox.question(
            self,
            "Выйти из сессии?",
            "Прогресс этой сессии не сохранится. Вы уверены?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.current_session_id:
                self.session_controller.delete_session(self.current_session_id)
            self.back_to_topics.emit()

    # =========================================================
    # ЛОГИРОВАНИЕ СОСТОЯНИЯ (вызывается вручную)
    # =========================================================

    def log_current_state(self):
        """Сохраняет текущие значения ползунков в БД"""
        if not self.current_session_id:
            return

        minute = self.timer.get_seconds() // 60

        self.session_controller.log_state(
            self.current_session_id,
            "concentration",
            self.state_sliders.get_concentration(),
            minute
        )
        self.session_controller.log_state(
            self.current_session_id,
            "energy",
            self.state_sliders.get_energy(),
            minute
        )
        self.session_controller.log_state(
            self.current_session_id,
            "interest",
            self.state_sliders.get_interest(),
            minute
        )

    # =========================================================
    # БЫСТРЫЕ ЗАПИСИ
    # =========================================================

    def show_quick_note_dialog(self):
        """Показывает диалог быстрой записи"""
        dialog = QuickNoteDialog(self)

        if dialog.exec():
            note_text = dialog.get_text()
            if note_text.strip():
                self.session_controller.add_quick_note(
                    self.current_session_id,
                    self.current_topic_id,
                    note_text
                )
                self.show_temp_message("✅ Запись сохранена!")

    def show_temp_message(self, message: str):
        """Показывает временное сообщение"""
        label = QLabel(message)
        label.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
            }
        """)
        label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(label)
        QTimer.singleShot(2000, label.deleteLater)

    # =========================================================
    # ЖИЗНЕННЫЙ ЦИКЛ
    # =========================================================

    def refresh(self):
        pass

    def cleanup(self):
        if self.current_session_id and self.timer.running:
            self.session_controller.delete_session(self.current_session_id)
            self.timer.reset()
