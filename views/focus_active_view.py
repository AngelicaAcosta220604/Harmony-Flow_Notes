# views/focus_active_view.py

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QDialog,
)
from PySide6.QtCore import Qt, QTimer, Signal
from widgets.silent_dialog import SilentMessageBox
from widgets.state_sliders import StateSliders
from widgets.custom_timer import CustomTimer
from widgets.music_widget import MusicWidget
from widgets.quick_note_dialog import QuickNoteDialog
from widgets.ping_dialog import PingDialog
from widgets.ping_manager import PingManager


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
        self.is_active = False

        # Создаём PingManager
        self.ping_manager = PingManager(idle_minutes=15, timeout_seconds=30)
        self.ping_manager.pingNeeded.connect(self._show_ping_dialog)
        self.ping_manager.timeoutReached.connect(self._auto_pause_from_ping)

        # Передаём ping_manager в session_controller
        self.session_controller.set_ping_manager(self.ping_manager)

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
            QPushButton:hover { background-color: #CC0000; }
        """)
        top_bar.addWidget(self.back_button)
        top_bar.addStretch()
        self.topic_label = QLabel()
        self.topic_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_bar.addWidget(self.topic_label)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        # ========== Центр: Таймер ==========
        self.timer = CustomTimer()
        main_layout.addWidget(self.timer, alignment=Qt.AlignCenter)

        # ========== Кнопки управления под таймером ==========
        control_buttons = QHBoxLayout()
        control_buttons.setAlignment(Qt.AlignCenter)
        control_buttons.setSpacing(15)

        # Кнопка паузы/плея
        self.play_pause_btn = QPushButton("⏸")
        self.play_pause_btn.setFixedSize(50, 50)
        self.play_pause_btn.setCursor(Qt.PointingHandCursor)
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #2C3E50;
                border: none;
                font-size: 28px;
            }
            QPushButton:hover {
                color: #FF9800;
            }
        """)
        control_buttons.addWidget(self.play_pause_btn)

        # Кнопка стоп
        self.stop_btn = QPushButton("⬤")
        self.stop_btn.setFixedSize(50, 50)
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #E74C3C;
                border: none;
                font-size: 24px;
            }
            QPushButton:hover {
                color: #C0392B;
            }
        """)
        control_buttons.addWidget(self.stop_btn)

        main_layout.addLayout(control_buttons)
        main_layout.addSpacing(20)

        # ========== Нижняя часть ==========
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(30)

        # ----- Левая колонка: Ползунки (без обводки) -----
        left_panel = QFrame()
        left_panel.setStyleSheet("QFrame { background-color: transparent; }")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)

        # Заголовок
        title_label = QLabel("📊 Твоё состояние")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2C3E50; margin-bottom: 5px;")
        left_layout.addWidget(title_label)

        self.state_sliders = StateSliders()
        left_layout.addWidget(self.state_sliders)

        hint_label = QLabel("💡 Меняй ползунки — изменения сохранятся автоматически")
        hint_label.setWordWrap(True)
        hint_label.setStyleSheet("color: #999; font-size: 10px; margin-top: 5px;")
        left_layout.addWidget(hint_label)

        bottom_row.addWidget(left_panel, stretch=2)

        # ----- Правая колонка: Кнопки -----
        right_panel = QFrame()
        right_panel.setStyleSheet("QFrame { background-color: transparent; }")
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

        right_layout.addStretch()
        self.music_widget = MusicWidget()
        right_layout.addWidget(self.music_widget)

        bottom_row.addWidget(right_panel, stretch=1)

        main_layout.addLayout(bottom_row)

    def connect_signals(self):
        """Подключает сигналы"""
        self.quick_note_btn.clicked.connect(self.show_quick_note_dialog)
        self.play_pause_btn.clicked.connect(self.toggle_pause)
        self.stop_btn.clicked.connect(self.end_session)
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
        self.is_active = True

        # Сбрасываем ползунки на 50 для новой сессии
        self.state_sliders.set_all(50, 50, 50)

        # Сохраняем начальные позиции в БД
        self.session_controller.save_slider_values(self.current_session_id, 50, 50, 50)

        # Сбрасываем таймер бездействия
        self.ping_manager.reset_idle()

        # Подключаем автосохранение ползунков
        self.state_sliders.connect_save_callback(self._auto_save_state)

        self.play_pause_btn.setText("⏸")
        self.play_pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)

    def _auto_save_state(self, metric: str, value: int):
        """Автоматическое сохранение состояния"""
        if not self.current_session_id:
            return

        minute = self.timer.get_seconds() // 60
        self.ping_manager.reset_idle()

        # Сохраняем лог состояния
        self.session_controller.log_state(
            self.current_session_id, metric, value, minute
        )

        # Сохраняем текущую позицию ползунка в сессию
        all_values = self.state_sliders.get_all_values()
        self.session_controller.save_slider_values(
            self.current_session_id,
            all_values["concentration"],
            all_values["energy"],
            all_values["interest"]
        )
        print(f"[DEBUG] Автосохранение: {metric}={value}, минута={minute}")

    def _show_ping_dialog(self):
        """Показывает диалог проверки активности"""
        dialog = PingDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.ping_manager.user_confirmed()
        else:
            self._auto_pause_from_ping()

    def _auto_pause_from_ping(self):
        """Автоматическая пауза при бездействии"""
        if self.current_session_id and self.is_active:
            self.timer.pause()
            self.session_controller.pause_session(self.current_session_id)
            self.play_pause_btn.setText("▶")
            self.is_active = False
            print("[DEBUG] Авто-пауза из-за бездействия")

    def toggle_pause(self):
        """Пауза / Возобновление"""
        if self.timer.running:
            self.timer.pause()
            self.session_controller.pause_session(self.current_session_id)
            self.play_pause_btn.setText("▶")
            self.is_active = False
        else:
            self.timer.resume()
            self.session_controller.resume_session(self.current_session_id)
            self.play_pause_btn.setText("⏸")
            self.is_active = True
        # Сбрасываем таймер бездействия
        self.ping_manager.reset_idle()

    def end_session(self):
        """Завершает сессию"""
        self.timer.pause()
        duration_seconds = self.timer.get_seconds()
        duration_minutes = duration_seconds // 60

        self.ping_manager.stop()
        self.session_controller.end_session(self.current_session_id, duration=duration_minutes)

        SilentMessageBox.information(self,
                                     "Сессия завершена",
                                     f"Сессия по теме '{self.current_topic_name}' завершена!\n\n"
                                     f"⏱ Длительность: {duration_minutes} минут"
                                     )

        self.session_ended.emit(self.current_session_id)
        self.current_session_id = None
        self.timer.reset()
        self.is_active = False

    def confirm_exit(self):
        """Подтверждение выхода из сессии (окно закрывается, но сессия продолжается)"""
        reply = SilentMessageBox.question(self,
                                          "Выйти из сессии?",
                                          "Сессия продолжится в фоне. Вы сможете вернуться позже."
                                          )
        if reply == QMessageBox.Yes:
            self.back_to_topics.emit()

    # =========================================================
    # ЛОГИРОВАНИЕ СОСТОЯНИЯ
    # =========================================================

    def log_current_state(self):
        """Сохраняет текущие значения ползунков в БД (вызывается вручную)"""
        if not self.current_session_id:
            return

        minute = self.timer.get_seconds() // 60

        self.ping_manager.reset_idle()

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

    def resume_existing_session(self, session_id: int, topic_id: int, topic_name: str):
        """Возобновляет существующую сессию"""
        print(f"[DEBUG] resume_existing_session: session_id={session_id}")

        self.current_session_id = session_id
        self.current_topic_id = topic_id
        self.current_topic_name = topic_name

        session = self.session_controller.get_session(session_id)
        if not session:
            return

        self.topic_label.setText(f"📚 {topic_name}")

        # Восстанавливаем позиции ползунков из БД
        slider_values = self.session_controller.get_slider_values(session_id)
        self.state_sliders.set_all(
            slider_values["concentration"],
            slider_values["energy"],
            slider_values["interest"]
        )
        print(
            f"[DEBUG] Восстановлены ползунки: концентрация={slider_values['concentration']}, энергия={slider_values['energy']}, интерес={slider_values['interest']}")

        if session.status in ("paused", "auto_paused"):
            total_seconds = session.total_active_seconds
            print(f"[DEBUG] PAUSED: total_active_seconds={total_seconds}")
            self.timer.set_seconds(total_seconds)
            self.timer.pause()
            self.play_pause_btn.setText("▶")
            self.play_pause_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 30px;
                    font-size: 24px;
                }
                QPushButton:hover { background-color: #45a049; }
            """)
            self.is_active = False
            self.session_controller.is_active = False

        elif session.status == "active":
            total_seconds = session.total_active_seconds
            print(f"[DEBUG] ACTIVE: total_active_seconds из БД={total_seconds}")

            if self.session_controller.session_resume_time:
                elapsed = int((datetime.now() - self.session_controller.session_resume_time).total_seconds())
                total_seconds += elapsed
                print(f"[DEBUG] ACTIVE: добавляем отрезок {elapsed} сек, итого={total_seconds}")

                from database.db_manager import db
                db.execute(
                    "UPDATE sessions SET total_active_seconds = ? WHERE id = ?",
                    (total_seconds, session_id)
                )

            self.timer.set_seconds(total_seconds)
            self.timer.start(total_seconds)
            self.play_pause_btn.setText("⏸")
            self.play_pause_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    border-radius: 30px;
                    font-size: 24px;
                }
                QPushButton:hover { background-color: #F57C00; }
            """)
            self.is_active = True
            self.session_controller.is_active = True
            self.session_controller.current_session_id = session_id
            self.session_controller.session_resume_time = datetime.now()

            print(f"[DEBUG] total_active_seconds из БД = {session.total_active_seconds}")
            print(f"[DEBUG] timer.get_seconds() = {self.timer.get_seconds()}")

        # Сбрасываем таймер бездействия
        self.ping_manager.reset_idle()
        self.play_pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)

    # =========================================================
    # БЫСТРЫЕ ЗАПИСИ
    # =========================================================

    def show_quick_note_dialog(self):
        """Показывает диалог быстрой записи"""
        # Сбрасываем таймер бездействия
        self.ping_manager.reset_idle()

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

    def refresh(self):
        pass

    def cleanup(self):
        """Очистка при закрытии окна"""
        self.ping_manager.stop()
        if self.current_session_id and self.timer.running:
            self.session_controller.delete_session(self.current_session_id)
            self.timer.reset()

    def stop_ping_manager(self):
        """Останавливает пинг-менеджер (вызывается при закрытии)"""
        self.ping_manager.stop()

    def force_save_state(self):
        """Принудительно сохраняет текущее состояние сессии (вызывается при закрытии)"""
        if self.current_session_id and self.is_active:
            # Сохраняем текущие значения ползунков
            all_values = self.state_sliders.get_all_values()
            self.session_controller.save_slider_values(
                self.current_session_id,
                all_values["concentration"],
                all_values["energy"],
                all_values["interest"]
            )
            print(f"[DEBUG] Принудительно сохранены ползунки: {all_values}")

    def force_save_time(self):
        """Принудительно сохраняет текущее время сессии в БД"""
        if self.current_session_id and self.timer.running:
            elapsed = self.timer.get_seconds()
            if elapsed > 0:
                from database.db_manager import db
                # Получаем текущее total_active_seconds
                current = db.fetchone("SELECT total_active_seconds FROM sessions WHERE id = ?",
                                      (self.current_session_id,))
                current_total = current["total_active_seconds"] if current else 0
                new_total = current_total + elapsed
                db.execute(
                    "UPDATE sessions SET total_active_seconds = ? WHERE id = ?",
                    (new_total, self.current_session_id)
                )
                print(f"[DEBUG] Принудительно сохранено время: +{elapsed} сек, всего={new_total} сек")