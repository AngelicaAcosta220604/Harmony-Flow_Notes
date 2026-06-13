# widgets/task_view_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QFrame, QCheckBox, QScrollArea, QMessageBox, QWidget
)
from PySide6.QtCore import Qt, Signal
from datetime import datetime

from services import TimeService
from widgets.silent_dialog import SilentMessageBox


class TaskViewDialog(QDialog):
    """Модальное окно для просмотра и редактирования задачи"""

    task_updated = Signal(int)  # сигнал об обновлении задачи
    task_deleted = Signal(int)  # сигнал об удалении задачи

    def __init__(self, task, task_controller, parent=None):
        super().__init__(parent)
        self.task = task
        self.task_controller = task_controller
        self.is_edit_mode = False

        self.setWindowTitle(f"Задача: {task.title}")
        self.setModal(True)
        self.setMinimumWidth(550)
        self.setMinimumHeight(500)

        self.setup_ui()
        self.apply_styles()
        self.update_display()

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # ========== Верхняя панель с кнопками ==========
        top_bar = QHBoxLayout()

        # Кнопка закрыть
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.accept)
        top_bar.addWidget(self.close_btn)

        top_bar.addStretch()

        # Кнопки редактирования и удаления (в режиме просмотра)
        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        top_bar.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.clicked.connect(self.delete_task)
        top_bar.addWidget(self.delete_btn)

        # Кнопки сохранения/отмены (в режиме редактирования)
        self.save_btn = QPushButton("✓ Сохранить")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_task)
        self.save_btn.setVisible(False)
        top_bar.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("✗ Отмена")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.toggle_edit_mode)
        self.cancel_btn.setVisible(False)
        top_bar.addWidget(self.cancel_btn)

        layout.addLayout(top_bar)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #E0E0E0; margin: 5px 0;")
        layout.addWidget(separator)

        # ========== Область с прокруткой для содержимого ==========
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(12)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll, 1)

        # ========== Статус (чекбокс) ==========
        status_frame = QFrame()
        status_frame.setStyleSheet("background-color: #F5F5F5; border-radius: 8px; padding: 8px;")
        status_layout = QHBoxLayout(status_frame)

        self.status_checkbox = QCheckBox("✅ Задача выполнена")
        self.status_checkbox.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.status_checkbox.stateChanged.connect(self._on_status_changed)
        status_layout.addWidget(self.status_checkbox)
        status_layout.addStretch()
        self.content_layout.addWidget(status_frame)

        # ========== Название ==========
        title_label = QLabel("📌 Название:")
        title_label.setStyleSheet("font-weight: bold; color: #555; margin-top: 5px;")
        self.content_layout.addWidget(title_label)

        self.title_display = QLabel()
        self.title_display.setWordWrap(True)
        self.title_display.setStyleSheet(
            "font-size: 16px; font-weight: bold; padding: 8px; background-color: #FAFAFA; border-radius: 6px; border: 1px solid #E0E0E0;")
        self.content_layout.addWidget(self.title_display)

        self.title_edit = QTextEdit()
        self.title_edit.setMaximumHeight(80)
        self.title_edit.setVisible(False)
        self.title_edit.setStyleSheet("border: 1px solid #CCC; border-radius: 6px; padding: 8px; font-size: 14px;")
        self.content_layout.addWidget(self.title_edit)

        # ========== Описание ==========
        desc_label = QLabel("📝 Описание:")
        desc_label.setStyleSheet("font-weight: bold; color: #555; margin-top: 10px;")
        self.content_layout.addWidget(desc_label)

        self.desc_display = QLabel()
        self.desc_display.setWordWrap(True)
        self.desc_display.setStyleSheet(
            "padding: 8px; background-color: #FAFAFA; border-radius: 6px; border: 1px solid #E0E0E0; color: #333; min-height: 80px;")
        self.desc_display.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.content_layout.addWidget(self.desc_display)

        self.desc_edit = QTextEdit()
        self.desc_edit.setVisible(False)
        self.desc_edit.setStyleSheet("border: 1px solid #CCC; border-radius: 6px; padding: 8px; min-height: 120px;")
        self.content_layout.addWidget(self.desc_edit)

        # ========== Дедлайн ==========
        deadline_label = QLabel("⏰ Дедлайн:")
        deadline_label.setStyleSheet("font-weight: bold; color: #555; margin-top: 10px;")
        self.content_layout.addWidget(deadline_label)

        self.deadline_display = QLabel()
        self.deadline_display.setStyleSheet(
            "padding: 8px; background-color: #FAFAFA; border-radius: 6px; border: 1px solid #E0E0E0; color: #666;")
        self.content_layout.addWidget(self.deadline_display)

        # Редактирование дедлайна
        from widgets.task_dialog import TaskDialog
        temp_dialog = TaskDialog()

        self.deadline_edit_widget = QWidget()
        deadline_edit_layout = QHBoxLayout(self.deadline_edit_widget)
        deadline_edit_layout.setContentsMargins(0, 0, 0, 0)

        self.deadline_date_edit = temp_dialog.deadline_date
        self.hour_combo = temp_dialog.hour_combo
        self.minute_combo = temp_dialog.minute_combo

        deadline_edit_layout.addWidget(self.deadline_date_edit)
        deadline_edit_layout.addWidget(QLabel(" "))
        deadline_edit_layout.addWidget(self.hour_combo)
        deadline_edit_layout.addWidget(QLabel(":"))
        deadline_edit_layout.addWidget(self.minute_combo)
        deadline_edit_layout.addStretch()

        self.deadline_edit_widget.setVisible(False)
        self.content_layout.addWidget(self.deadline_edit_widget)

        # ========== Дата создания ==========
        created_label = QLabel("📅 Создана:")
        created_label.setStyleSheet("font-weight: bold; color: #555; margin-top: 10px;")
        self.content_layout.addWidget(created_label)

        self.created_display = QLabel()
        self.created_display.setStyleSheet("padding: 5px; color: #999; font-size: 11px;")
        self.content_layout.addWidget(self.created_display)

        self.content_layout.addStretch()

    def apply_styles(self):
        """Применяет стили для кнопок"""
        btn_style = """
            QPushButton {
                padding: 6px 14px;
                border: 1px solid #CCC;
                border-radius: 6px;
                background-color: #f5f5f5;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """

        self.edit_btn.setStyleSheet(btn_style)
        self.delete_btn.setStyleSheet(btn_style)
        self.save_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 14px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 14px;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)

    def update_display(self):
        """Обновляет отображение данных задачи"""
        # Статус
        self.status_checkbox.setChecked(self.task.status == "completed")

        # Название
        self.title_display.setText(self.task.title)
        self.title_edit.setPlainText(self.task.title)

        # Описание
        if self.task.description and self.task.description.strip():
            self.desc_display.setText(self.task.description)
            self.desc_edit.setPlainText(self.task.description)
        else:
            self.desc_display.setText("<нет описания>")
            self.desc_edit.setPlainText("")

        # Дедлайн
        if self.task.deadline:
            try:
                deadline_dt = datetime.fromisoformat(self.task.deadline)
                self.deadline_display.setText(TimeService.format_display(self.task.deadline))
                self.deadline_date_edit.setDate(deadline_dt.date())
                self.hour_combo.setCurrentText(f"{deadline_dt.hour:02d}")
                self.minute_combo.setCurrentText(f"{deadline_dt.minute:02d}")
            except:
                self.deadline_display.setText("не указан")
        else:
            self.deadline_display.setText("не указан")

        # Дата создания
        if self.task.created_at:
            self.created_display.setText(TimeService.format_display(self.task.created_at))

    def toggle_edit_mode(self):
        """Переключает режим редактирования"""
        self.is_edit_mode = not self.is_edit_mode

        # Переключаем видимость элементов
        self.title_display.setVisible(not self.is_edit_mode)
        self.title_edit.setVisible(self.is_edit_mode)
        self.desc_display.setVisible(not self.is_edit_mode)
        self.desc_edit.setVisible(self.is_edit_mode)
        self.deadline_display.setVisible(not self.is_edit_mode)
        self.deadline_edit_widget.setVisible(self.is_edit_mode)

        # Переключаем кнопки
        self.edit_btn.setVisible(not self.is_edit_mode)
        self.delete_btn.setVisible(not self.is_edit_mode)
        self.save_btn.setVisible(self.is_edit_mode)
        self.cancel_btn.setVisible(self.is_edit_mode)

        if self.is_edit_mode:
            self.title_edit.setPlainText(self.task.title)
            self.desc_edit.setPlainText(self.task.description or "")
        else:
            self.update_display()

    def save_task(self):
        """Сохраняет изменения задачи"""
        new_title = self.title_edit.toPlainText().strip()
        if not new_title:
            SilentMessageBox.warning(self, "Ошибка", "Название задачи не может быть пустым!")
            return

        new_description = self.desc_edit.toPlainText().strip()

        # Формируем дедлайн
        if self.deadline_edit_widget.isVisible():
            date = self.deadline_date_edit.date()
            hour = self.hour_combo.currentData()
            minute = self.minute_combo.currentData()
            deadline_str = f"{date.year()}-{date.month():02d}-{date.day():02d} {hour:02d}:{minute:02d}:00"
        else:
            deadline_str = None

        self.task_controller.update_task(
            task_id=self.task.id,
            title=new_title,
            description=new_description,
            deadline=deadline_str
        )

        # Обновляем локальные данные
        self.task.title = new_title
        self.task.description = new_description
        self.task.deadline = deadline_str

        self.toggle_edit_mode()
        self.task_updated.emit(self.task.id)
        SilentMessageBox.information(self, "Готово", "Задача обновлена!")

    def delete_task(self):
        """Удаляет задачу"""
        reply = SilentMessageBox.question(
            self, "Удаление",
            f"Вы уверены, что хотите удалить задачу «{self.task.title}»?"
        )
        if reply == QMessageBox.Yes:
            task_id = self.task.id
            self.task_controller.delete_task(task_id)
            self.task_deleted.emit(task_id)
            self.accept()

    def _on_status_changed(self, state: int):
        """Обработчик изменения статуса (чекбокс)"""
        status = "completed" if state == 2 else "active"
        if self.task.status != status:
            self.task_controller.update_task_status(self.task.id, status)
            self.task.status = status
            self.task_updated.emit(self.task.id)
            self.update_display()