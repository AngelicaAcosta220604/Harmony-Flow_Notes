# views/base_tasks_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QComboBox,
    QCheckBox, QDateEdit, QMessageBox, QSizePolicy,
    QButtonGroup
)
from widgets.silent_dialog import SilentMessageBox
from PySide6.QtCore import Qt, Signal, QDate, QTimer
from datetime import datetime

from services import TimeService
from widgets.task_dialog import TaskDialog


class BaseTasksView(QWidget):
    """Базовый класс для отображения задач (глобально или по теме)"""

    tasks_updated = Signal()
    task_added = Signal(object)
    task_changed = Signal(int)
    task_deleted = Signal(int)

    def __init__(self, task_controller, parent=None):
        super().__init__(parent)
        self.task_controller = task_controller

        self.current_tasks = []
        self.current_filter = "all"  # all, active, completed, overdue
        self.current_period = "all"  # all, month, week, day
        self.current_date = QDate.currentDate()

        # Таймер для автоматического обновления (каждые 30 секунд)
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.load_tasks)
        self.auto_refresh_timer.start(30000)

        # Русские названия месяцев
        self.month_names = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }

        self.setup_ui()
        self.apply_styles()

        self.load_tasks()

    def setup_ui(self):
        """Настройка интерфейса"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ========== Верхняя панель ==========
        top_panel = QWidget()
        top_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        top_layout = QVBoxLayout(top_panel)
        top_layout.setContentsMargins(15, 15, 15, 10)
        top_layout.setSpacing(15)

        # Строка с кнопкой создания
        top_bar = QHBoxLayout()
        self.create_btn = QPushButton("+ Новая задача")
        self.create_btn.setMinimumHeight(34)
        self.create_btn.clicked.connect(self.create_task)
        top_bar.addWidget(self.create_btn)
        top_bar.addStretch()
        top_layout.addLayout(top_bar)

        # ========== Панель фильтров (как в темах) ==========
        # Фильтр по статусу
        status_label = QLabel("Статус:")
        status_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #555;")
        top_layout.addWidget(status_label)

        status_filters = QHBoxLayout()
        status_filters.setSpacing(10)

        # Создаем кнопки-переключатели для статуса
        self.btn_all = QPushButton("📋 Все")
        self.btn_active = QPushButton("🟢 Активные")
        self.btn_completed = QPushButton("✅ Выполненные")
        self.btn_overdue = QPushButton("🔴 Просроченные")

        filter_style = """
            QPushButton {
                padding: 6px 16px;
                border: 1px solid #DDD;
                border-radius: 20px;
                font-size: 12px;
                background-color: white;
            }
            QPushButton:checked {
                background-color: #51b2c1;
                color: white;
                border-color: #51b2c1;
            }
            QPushButton:hover:!checked {
                background-color: #f0f0f0;
            }
        """

        self.btn_all.setCheckable(True)
        self.btn_active.setCheckable(True)
        self.btn_completed.setCheckable(True)
        self.btn_overdue.setCheckable(True)
        self.btn_all.setChecked(True)

        self.btn_all.setStyleSheet(filter_style)
        self.btn_active.setStyleSheet(filter_style)
        self.btn_completed.setStyleSheet(filter_style)
        self.btn_overdue.setStyleSheet(filter_style)

        self.btn_all.clicked.connect(lambda: self._set_status_filter("all"))
        self.btn_active.clicked.connect(lambda: self._set_status_filter("active"))
        self.btn_completed.clicked.connect(lambda: self._set_status_filter("completed"))
        self.btn_overdue.clicked.connect(lambda: self._set_status_filter("overdue"))

        status_filters.addWidget(self.btn_all)
        status_filters.addWidget(self.btn_active)
        status_filters.addWidget(self.btn_completed)
        status_filters.addWidget(self.btn_overdue)
        status_filters.addStretch()
        top_layout.addLayout(status_filters)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #E0E0E0; max-height: 1px;")
        top_layout.addWidget(separator)

        # ========== Панель периода ==========
        period_label = QLabel("Период:")
        period_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #555; margin-top: 5px;")
        top_layout.addWidget(period_label)

        period_filters = QHBoxLayout()
        period_filters.setSpacing(10)

        self.btn_period_all = QPushButton("📋 Все задачи")
        self.btn_period_month = QPushButton("📅 Месяц")
        self.btn_period_week = QPushButton("📆 Неделя")
        self.btn_period_day = QPushButton("📌 День")

        period_style = """
            QPushButton {
                padding: 6px 16px;
                border: 1px solid #DDD;
                border-radius: 20px;
                font-size: 12px;
                background-color: white;
            }
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
                border-color: #4CAF50;
            }
            QPushButton:hover:!checked {
                background-color: #f0f0f0;
            }
        """

        self.btn_period_all.setCheckable(True)
        self.btn_period_month.setCheckable(True)
        self.btn_period_week.setCheckable(True)
        self.btn_period_day.setCheckable(True)
        self.btn_period_all.setChecked(True)

        for btn in [self.btn_period_all, self.btn_period_month, self.btn_period_week, self.btn_period_day]:
            btn.setStyleSheet(period_style)

        self.btn_period_all.clicked.connect(lambda: self._set_period("all"))
        self.btn_period_month.clicked.connect(lambda: self._set_period("month"))
        self.btn_period_week.clicked.connect(lambda: self._set_period("week"))
        self.btn_period_day.clicked.connect(lambda: self._set_period("day"))

        period_filters.addWidget(self.btn_period_all)
        period_filters.addWidget(self.btn_period_month)
        period_filters.addWidget(self.btn_period_week)
        period_filters.addWidget(self.btn_period_day)
        period_filters.addStretch()
        top_layout.addLayout(period_filters)

        # ========== Панель навигации (для месяца/недели/дня) ==========
        nav_panel = QWidget()
        nav_layout = QHBoxLayout(nav_panel)
        nav_layout.setContentsMargins(0, 5, 0, 5)

        self.nav_left_btn = QPushButton("◀")
        self.nav_left_btn.setFixedSize(30, 28)
        self.nav_left_btn.clicked.connect(self._nav_previous)
        nav_layout.addWidget(self.nav_left_btn)

        self.period_title = QLabel()
        self.period_title.setStyleSheet("font-size: 14px; font-weight: bold; min-width: 200px;")
        self.period_title.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(self.period_title)

        self.nav_right_btn = QPushButton("▶")
        self.nav_right_btn.setFixedSize(30, 28)
        self.nav_right_btn.clicked.connect(self._nav_next)
        nav_layout.addWidget(self.nav_right_btn)

        nav_layout.addSpacing(30)
        nav_layout.addWidget(QLabel("Перейти к дате:"))

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        self.date_edit.setFixedWidth(120)
        self.date_edit.dateChanged.connect(self._on_date_changed)
        nav_layout.addWidget(self.date_edit)
        nav_layout.addStretch()

        nav_panel.setVisible(False)
        top_layout.addWidget(nav_panel)

        main_layout.addWidget(top_panel)

        # ========== Скроллируемая область для задач ==========
        self.tasks_scroll = QScrollArea()
        self.tasks_scroll.setWidgetResizable(True)
        self.tasks_scroll.setFrameShape(QFrame.NoFrame)
        self.tasks_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tasks_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #FAFAFA;
            }
            QScrollBar:vertical {
                width: 10px;
                background: #f0f0f0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
        """)

        self.tasks_container = QWidget()
        self.tasks_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setAlignment(Qt.AlignTop)
        self.tasks_layout.setSpacing(10)
        self.tasks_layout.setContentsMargins(15, 10, 15, 10)

        self.tasks_scroll.setWidget(self.tasks_container)
        main_layout.addWidget(self.tasks_scroll, 1)

        # Сохраняем ссылки на виджеты
        self.nav_panel = nav_panel

        self._update_navigation_visibility()

    def apply_styles(self):
        """Применяет стили для кнопок"""
        self.create_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        nav_style = """
            QPushButton {
                padding: 4px 12px;
                border: 1px solid #CCC;
                border-radius: 4px;
                font-size: 12px;
                background-color: #f8f8f8;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """
        self.nav_left_btn.setStyleSheet(nav_style)
        self.nav_right_btn.setStyleSheet(nav_style)

    def _set_status_filter(self, filter_type: str):
        """Устанавливает фильтр по статусу"""
        self.current_filter = filter_type
        self.btn_all.setChecked(filter_type == "all")
        self.btn_active.setChecked(filter_type == "active")
        self.btn_completed.setChecked(filter_type == "completed")
        self.btn_overdue.setChecked(filter_type == "overdue")
        self.load_tasks()

    def _update_navigation_visibility(self):
        """Обновляет видимость навигационных стрелок"""
        show_nav = self.current_period != "all"
        self.nav_panel.setVisible(show_nav)

        if self.current_period == "month":
            month_ru = self.month_names.get(self.current_date.month(), "")
            self.period_title.setText(f"{month_ru} {self.current_date.year()}")
        elif self.current_period == "week":
            days_to_monday = self.current_date.dayOfWeek() - 1
            start_date = self.current_date.addDays(-days_to_monday)
            end_date = start_date.addDays(6)
            self.period_title.setText(f"{start_date.toString('dd.MM')} - {end_date.toString('dd.MM.yyyy')}")
        elif self.current_period == "day":
            self.period_title.setText(self.current_date.toString("dd.MM.yyyy"))
        else:
            self.period_title.setText("Все задачи")

    def _set_period(self, period: str):
        """Переключает период отображения"""
        self.current_period = period
        self.btn_period_all.setChecked(period == "all")
        self.btn_period_month.setChecked(period == "month")
        self.btn_period_week.setChecked(period == "week")
        self.btn_period_day.setChecked(period == "day")
        self._update_navigation_visibility()
        self.load_tasks()

    def _nav_previous(self):
        """Переход к предыдущему периоду"""
        if self.current_period == "month":
            self.current_date = self.current_date.addMonths(-1)
        elif self.current_period == "week":
            self.current_date = self.current_date.addDays(-7)
        elif self.current_period == "day":
            self.current_date = self.current_date.addDays(-1)
        self.date_edit.setDate(self.current_date)
        self.load_tasks()

    def _nav_next(self):
        """Переход к следующему периоду"""
        if self.current_period == "month":
            self.current_date = self.current_date.addMonths(1)
        elif self.current_period == "week":
            self.current_date = self.current_date.addDays(7)
        elif self.current_period == "day":
            self.current_date = self.current_date.addDays(1)
        self.date_edit.setDate(self.current_date)
        self.load_tasks()

    def _on_date_changed(self, date: QDate):
        """Обработчик изменения даты"""
        self.current_date = date
        self.load_tasks()

    def _get_date_range(self):
        """Возвращает начальную и конечную дату для текущего периода"""
        if self.current_period == "day":
            return self.current_date, self.current_date
        elif self.current_period == "week":
            days_to_monday = self.current_date.dayOfWeek() - 1
            start_date = self.current_date.addDays(-days_to_monday)
            return start_date, start_date.addDays(6)
        elif self.current_period == "month":
            start_date = QDate(self.current_date.year(), self.current_date.month(), 1)
            return start_date, QDate(self.current_date.year(), self.current_date.month(), start_date.daysInMonth())
        else:
            return None, None

    def get_tasks(self):
        """Метод для получения задач - должен быть переопределен в наследниках"""
        raise NotImplementedError("Метод get_tasks должен быть переопределен в наследнике")

    def load_tasks(self):
        """Загружает и отображает задачи"""
        start_date, end_date = self._get_date_range()

        # Получаем задачи через метод наследника
        all_tasks = self.get_tasks()

        # Фильтруем по дате дедлайна (если период не "all")
        period_tasks = []
        for task in all_tasks:
            if self.current_period == "all":
                period_tasks.append(task)
            elif task.deadline:
                try:
                    deadline_date = QDate.fromString(task.deadline[:10], "yyyy-MM-dd")
                    if deadline_date >= start_date and deadline_date <= end_date:
                        period_tasks.append(task)
                except:
                    pass

        # Обновляем статус просроченных
        now = datetime.now()
        for task in period_tasks:
            if task.status == "active" and task.deadline:
                try:
                    deadline_dt = datetime.fromisoformat(task.deadline)
                    if deadline_dt < now:
                        task.status = "overdue"
                except:
                    pass

        # Фильтруем по статусу
        if self.current_filter == "active":
            self.current_tasks = [t for t in period_tasks if t.status == "active"]
        elif self.current_filter == "completed":
            self.current_tasks = [t for t in period_tasks if t.status == "completed"]
        elif self.current_filter == "overdue":
            self.current_tasks = [t for t in period_tasks if t.status == "overdue"]
        else:
            self.current_tasks = period_tasks

        # Сортируем по дате дедлайна
        def task_date_key(task):
            if task.deadline:
                try:
                    return datetime.fromisoformat(task.deadline)
                except:
                    return datetime.max
            return datetime.max

        self.current_tasks.sort(key=task_date_key)
        self.display_tasks()

    def display_tasks(self):
        """Отображает задачи в виде карточек"""
        # Сохраняем позицию скролла
        scroll_pos = self.tasks_scroll.verticalScrollBar().value()

        # Очищаем контейнер
        while self.tasks_layout.count():
            item = self.tasks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.current_tasks:
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_layout.setAlignment(Qt.AlignCenter)

            empty_text = "✨ Нет задач ✨"
            if self.current_period != "all":
                empty_text = f"📭 Нет задач за выбранный период 📭"

            empty_label = QLabel(empty_text)
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #999; font-size: 16px; padding: 50px;")
            empty_layout.addWidget(empty_label)

            self.tasks_layout.addWidget(empty_widget)
        else:
            for task in self.current_tasks:
                task_widget = self._create_task_card(task)
                self.tasks_layout.addWidget(task_widget)

        # Восстанавливаем позицию скролла
        self.tasks_scroll.verticalScrollBar().setValue(scroll_pos)

    def _get_deadline_status(self, deadline_str):
        """Возвращает статус дедлайна для подсветки"""
        if not deadline_str:
            return "none"

        try:
            deadline = datetime.fromisoformat(deadline_str)
            now = datetime.now()

            if deadline < now:
                return "overdue"

            time_left = deadline - now
            if time_left.total_seconds() < 24 * 3600:
                return "urgent"
            elif time_left.total_seconds() < 48 * 3600:
                return "warning"
            return "normal"
        except:
            return "none"

    def _create_task_card(self, task):
        """Создаёт карточку задачи"""
        task_frame = QFrame()
        task_frame.setFrameShape(QFrame.Box)
        task_frame.setObjectName(f"task_{task.id}")

        deadline_status = self._get_deadline_status(task.deadline)
        is_completed = task.status == "completed"

        # Стиль рамки в зависимости от статуса
        if is_completed:
            task_frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #4CAF50;
                    border-radius: 10px;
                    padding: 12px;
                    background-color: #e8f5e9;
                }
                QFrame:hover {
                    background-color: #c8e6c9;
                    border-color: #388E3C;
                }
            """)
        elif deadline_status == "overdue":
            task_frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #f44336;
                    border-radius: 10px;
                    padding: 12px;
                    background-color: #ffebee;
                }
                QFrame:hover {
                    background-color: #ffcdd2;
                    border-color: #d32f2f;
                }
            """)
        elif deadline_status == "urgent":
            task_frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #ff9800;
                    border-radius: 10px;
                    padding: 12px;
                    background-color: #fff3e0;
                }
                QFrame:hover {
                    background-color: #ffe0b2;
                    border-color: #f57c00;
                }
            """)
        else:
            task_frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #E0E0E0;
                    border-radius: 10px;
                    padding: 12px;
                    background-color: white;
                }
                QFrame:hover {
                    background-color: #fafafa;
                    border-color: #BDBDBD;
                }
            """)

        layout = QVBoxLayout(task_frame)
        layout.setSpacing(8)

        # ========== Верхняя строка ==========
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Чекбокс для быстрого изменения статуса
        checkbox = QCheckBox()
        checkbox.setChecked(is_completed)
        checkbox.stateChanged.connect(lambda state, tid=task.id: self._toggle_task_status(tid, state))
        header_layout.addWidget(checkbox)

        # Название задачи
        title_label = QLabel(task.title)
        title_style = "font-size: 15px; font-weight: bold;"
        if is_completed:
            title_style += " text-decoration: line-through; color: #4CAF50;"
        title_label.setStyleSheet(title_style)
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label, stretch=1)

        # Бейдж дедлайна (только если не выполнена)
        if not is_completed and task.deadline:
            try:
                deadline_label = QLabel(f"📅 {TimeService.format_display(task.deadline)}")

                if deadline_status == "overdue":
                    deadline_label.setStyleSheet(
                        "color: #f44336; font-size: 11px; font-weight: bold; padding: 2px 8px; background-color: #ffebee; border-radius: 12px;")
                elif deadline_status == "urgent":
                    deadline_label.setStyleSheet(
                        "color: #ff9800; font-size: 11px; font-weight: bold; padding: 2px 8px; background-color: #fff3e0; border-radius: 12px;")
                elif deadline_status == "warning":
                    deadline_label.setStyleSheet(
                        "color: #ffc107; font-size: 11px; padding: 2px 8px; background-color: #fff8e1; border-radius: 12px;")
                else:
                    deadline_label.setStyleSheet(
                        "color: #757575; font-size: 11px; padding: 2px 8px; background-color: #f5f5f5; border-radius: 12px;")

                header_layout.addWidget(deadline_label)
            except:
                pass

        # Бейдж "Выполнена"
        if is_completed:
            completed_label = QLabel("✅ Выполнена")
            completed_label.setStyleSheet(
                "color: #4CAF50; font-size: 11px; font-weight: bold; padding: 2px 8px; background-color: #e8f5e9; border-radius: 12px;")
            header_layout.addWidget(completed_label)

        layout.addLayout(header_layout)

        # ========== Описание (предпросмотр) ==========
        if task.description:
            preview = task.description[:100]
            if len(task.description) > 100:
                preview += "..."
            desc_preview = QLabel(preview)
            desc_preview.setWordWrap(True)
            desc_preview.setStyleSheet("color: #666; font-size: 12px; margin-left: 28px;")
            layout.addWidget(desc_preview)

        # ========== Дата создания (маленькая) ==========
        if task.created_at:
            try:
                created_label = QLabel(f"📝 {TimeService.format_display(task.created_at)}")
                created_label.setStyleSheet("color: #999; font-size: 10px; margin-left: 28px;")
                layout.addWidget(created_label)
            except:
                pass

        # ========== Обработчик клика по карточке ==========
        def on_card_click(event):
            # Проверяем, что клик не по чекбоксу и не по дочерним виджетам-кнопкам
            pos = event.pos()
            child = task_frame.childAt(pos)

            # Если клик по чекбоксу или его области - не открываем диалог
            if child and isinstance(child, QCheckBox):
                return

            # Проверяем всех родителей, чтобы убедиться, что клик не по чекбоксу
            current = child
            while current:
                if isinstance(current, QCheckBox):
                    return
                current = current.parent()

            self._open_task_view(task.id)

        task_frame.mousePressEvent = on_card_click

        return task_frame

    def _toggle_task_status(self, task_id: int, state: int):
        """Переключает статус задачи"""
        status = "completed" if state == 2 else "active"
        self.task_controller.update_task_status(task_id, status)
        self.load_tasks()
        self.tasks_updated.emit()
        self.task_changed.emit(task_id)

    def create_task(self):
        """Создаёт новую задачу - должен быть переопределен в наследниках"""
        raise NotImplementedError("Метод create_task должен быть переопределен в наследнике")

    def edit_task(self, task_id: int):
        """Редактирует задачу"""
        task = next((t for t in self.current_tasks if t.id == task_id), None)
        if not task:
            return

        dialog = TaskDialog(self)
        dialog.setWindowTitle("Редактировать задачу")
        dialog.title_input.setText(task.title)
        dialog.desc_input.setPlainText(task.description or "")

        if task.deadline:
            try:
                deadline_dt = datetime.fromisoformat(task.deadline)
                dialog.deadline_date.setDate(QDate(deadline_dt.year, deadline_dt.month, deadline_dt.day))
                dialog.hour_combo.setCurrentText(f"{deadline_dt.hour:02d}")
                dialog.minute_combo.setCurrentText(f"{deadline_dt.minute:02d}")
                dialog.no_deadline_check.setChecked(False)
            except:
                dialog.no_deadline_check.setChecked(True)
        else:
            dialog.no_deadline_check.setChecked(True)

        if dialog.exec():
            new_title = dialog.get_title()
            if new_title:
                self.task_controller.update_task(
                    task_id=task_id,
                    title=new_title,
                    description=dialog.get_description(),
                    deadline=dialog.get_deadline()
                )
                self.load_tasks()
                self.tasks_updated.emit()
                self.task_changed.emit(task_id)
                SilentMessageBox.information(self, "Готово", "Задача обновлена!")

    def _open_task_view(self, task_id: int):
        """Открывает модальное окно просмотра задачи"""
        from widgets.task_view_dialog import TaskViewDialog  # ← этот импорт правильный

        task = next((t for t in self.current_tasks if t.id == task_id), None)
        if not task:
            return

        dialog = TaskViewDialog(task, self.task_controller, self)
        dialog.task_updated.connect(self._on_task_updated_from_dialog)
        dialog.task_deleted.connect(self._on_task_deleted_from_dialog)
        dialog.exec()

    def _on_task_updated_from_dialog(self, task_id: int):
        """Обработчик обновления задачи из диалога"""
        self.load_tasks()
        self.tasks_updated.emit()
        self.task_changed.emit(task_id)

    def _on_task_deleted_from_dialog(self, task_id: int):
        """Обработчик удаления задачи из диалога"""
        self.load_tasks()
        self.tasks_updated.emit()
        self.task_deleted.emit(task_id)

    def delete_task(self, task_id: int):
        """Удаляет задачу"""
        reply = SilentMessageBox.question(self, "Удаление", "Вы уверены, что хотите удалить эту задачу?")
        if reply == QMessageBox.Yes:
            self.task_controller.delete_task(task_id)
            self.load_tasks()
            self.tasks_updated.emit()
            self.task_deleted.emit(task_id)

    def refresh(self):
        """Обновляет список задач"""
        self.load_tasks()

    def cleanup(self):
        """Очистка таймера при закрытии"""
        if self.auto_refresh_timer:
            self.auto_refresh_timer.stop()
