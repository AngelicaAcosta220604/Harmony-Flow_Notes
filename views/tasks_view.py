# views/tasks_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QComboBox,
    QCheckBox, QDateEdit, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QDate, QDateTime
from datetime import datetime, timedelta
from widgets.task_dialog import TaskDialog


class TasksView(QWidget):
    """Виджет для отображения и управления задачами темы."""

    tasks_updated = Signal()

    def __init__(self, task_controller, topic_id: int, parent=None):
        super().__init__(parent)
        self.task_controller = task_controller
        self.topic_id = topic_id

        self.current_tasks = []
        self.current_filter = "all"  # all, active, completed, overdue
        self.current_period = "all"  # all, month, week, day (по умолчанию all)
        self.current_date = QDate.currentDate()

        # Русские названия месяцев
        self.month_names = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }

        self.setup_ui()
        self.load_tasks()

    def setup_ui(self):
        """Настройка интерфейса."""
        layout = QVBoxLayout(self)

        # ========== Верхняя панель ==========
        top_bar = QHBoxLayout()

        # Кнопка создания задачи
        self.create_btn = QPushButton("+ Новая задача")
        self.create_btn.clicked.connect(self.create_task)
        top_bar.addWidget(self.create_btn)

        top_bar.addSpacing(20)

        # Фильтр по статусу
        filter_label = QLabel("Фильтр:")
        filter_label.setStyleSheet("font-size: 12px;")
        top_bar.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("📋 Все", "all")
        self.filter_combo.addItem("🟢 Активные", "active")
        self.filter_combo.addItem("✅ Выполненные", "completed")
        self.filter_combo.addItem("🔴 Просроченные", "overdue")
        self.filter_combo.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #CCC;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
        """)
        self.filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        top_bar.addWidget(self.filter_combo)

        top_bar.addStretch()
        layout.addLayout(top_bar)

        # ========== Панель выбора периода ==========
        period_bar = QHBoxLayout()

        # Кнопки переключения периода
        self.btn_all = QPushButton("📋 Все задачи")
        self.btn_month = QPushButton("📅 Месяц")
        self.btn_week = QPushButton("📆 Неделя")
        self.btn_day = QPushButton("📌 День")

        self.btn_all.setCheckable(True)
        self.btn_month.setCheckable(True)
        self.btn_week.setCheckable(True)
        self.btn_day.setCheckable(True)
        self.btn_all.setChecked(True)

        period_style = """
            QPushButton {
                padding: 6px 12px;
                border: 1px solid #CCC;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:checked {
                background-color: #51b2c1;
                color: white;
                border-color: #51b2c1;
            }
        """
        self.btn_all.setStyleSheet(period_style)
        self.btn_month.setStyleSheet(period_style)
        self.btn_week.setStyleSheet(period_style)
        self.btn_day.setStyleSheet(period_style)

        self.btn_all.clicked.connect(lambda: self._set_period("all"))
        self.btn_month.clicked.connect(lambda: self._set_period("month"))
        self.btn_week.clicked.connect(lambda: self._set_period("week"))
        self.btn_day.clicked.connect(lambda: self._set_period("day"))

        period_bar.addWidget(self.btn_all)
        period_bar.addWidget(self.btn_month)
        period_bar.addWidget(self.btn_week)
        period_bar.addWidget(self.btn_day)

        period_bar.addStretch()
        layout.addLayout(period_bar)

        # ========== Панель навигации (отдельная строка) ==========
        nav_bar = QHBoxLayout()

        # Кнопка навигации влево
        self.nav_left_btn = QPushButton("◀")
        self.nav_left_btn.setFixedSize(30, 28)
        self.nav_left_btn.clicked.connect(self._nav_previous)
        nav_bar.addWidget(self.nav_left_btn)

        # Надпись с текущим периодом (будет обновляться)
        self.period_title = QLabel()
        self.period_title.setStyleSheet("font-size: 14px; font-weight: bold; min-width: 200px;")
        self.period_title.setAlignment(Qt.AlignCenter)
        nav_bar.addWidget(self.period_title)

        # Кнопка навигации вправо
        self.nav_right_btn = QPushButton("▶")
        self.nav_right_btn.setFixedSize(30, 28)
        self.nav_right_btn.clicked.connect(self._nav_next)
        nav_bar.addWidget(self.nav_right_btn)

        # Выбор конкретной даты (маленький календарь)
        nav_bar.addSpacing(30)
        nav_bar.addWidget(QLabel("Перейти к дате:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        self.date_edit.setFixedWidth(120)
        self.date_edit.dateChanged.connect(self._on_date_changed)
        nav_bar.addWidget(self.date_edit)

        nav_bar.addStretch()
        layout.addLayout(nav_bar)

        # Скрываем навигацию по умолчанию (пока режим "Все задачи")
        self.nav_left_btn.setVisible(False)
        self.nav_right_btn.setVisible(False)

        # ========== Список задач ==========
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setAlignment(Qt.AlignTop)
        self.tasks_layout.setSpacing(8)

        self.scroll_area.setWidget(self.tasks_container)
        layout.addWidget(self.scroll_area)

    def _update_navigation_visibility(self):
        """Обновляет видимость навигационных стрелок и заголовок периода."""
        show_nav = self.current_period != "all"
        self.nav_left_btn.setVisible(show_nav)
        self.nav_right_btn.setVisible(show_nav)

        # Обновляем заголовок
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
        """Переключает период отображения."""
        self.current_period = period
        self.btn_all.setChecked(period == "all")
        self.btn_month.setChecked(period == "month")
        self.btn_week.setChecked(period == "week")
        self.btn_day.setChecked(period == "day")

        # Обновляем видимость навигации
        self._update_navigation_visibility()

        # Если переключились на "Все задачи" — сбрасываем навигацию
        if period == "all":
            self.load_tasks()
        else:
            # Синхронизируем date_edit с текущим периодом
            self.date_edit.setDate(self.current_date)
            self.load_tasks()

    def _nav_previous(self):
        """Переход к предыдущему периоду."""
        if self.current_period == "month":
            self.current_date = self.current_date.addMonths(-1)
        elif self.current_period == "week":
            self.current_date = self.current_date.addDays(-7)
        elif self.current_period == "day":
            self.current_date = self.current_date.addDays(-1)

        self.date_edit.setDate(self.current_date)
        self._update_navigation_visibility()
        self.load_tasks()

    def _nav_next(self):
        """Переход к следующему периоду."""
        if self.current_period == "month":
            self.current_date = self.current_date.addMonths(1)
        elif self.current_period == "week":
            self.current_date = self.current_date.addDays(7)
        elif self.current_period == "day":
            self.current_date = self.current_date.addDays(1)

        self.date_edit.setDate(self.current_date)
        self._update_navigation_visibility()
        self.load_tasks()

    def _on_date_changed(self, date: QDate):
        """Обработчик изменения даты."""
        self.current_date = date
        self._update_navigation_visibility()
        self.load_tasks()

    def _on_filter_changed(self):
        """Обработчик изменения фильтра."""
        self.current_filter = self.filter_combo.currentData()
        self.load_tasks()

    def _get_date_range(self):
        """Возвращает начальную и конечную дату для текущего периода."""
        today = self.current_date

        if self.current_period == "day":
            start_date = today
            end_date = today
        elif self.current_period == "week":
            days_to_monday = today.dayOfWeek() - 1
            start_date = today.addDays(-days_to_monday)
            end_date = start_date.addDays(6)
        elif self.current_period == "month":
            start_date = QDate(today.year(), today.month(), 1)
            end_date = QDate(today.year(), today.month(), start_date.daysInMonth())
        else:  # all
            start_date = None
            end_date = None

        return start_date, end_date

    def load_tasks(self):
        """Загружает и отображает задачи."""
        start_date, end_date = self._get_date_range()

        # Получаем все задачи темы
        all_tasks = self.task_controller.get_tasks_by_topic(self.topic_id)

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
            else:
                # Задачи без дедлайна показываем только в режиме "all"
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
        """Отображает задачи в виде карточек."""
        # Очищаем контейнер
        while self.tasks_layout.count():
            item = self.tasks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.current_tasks:
            empty_text = "Нет задач"
            if self.current_period != "all":
                empty_text = "Нет задач за выбранный период"
            empty_label = QLabel(empty_text)
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: gray; padding: 40px;")
            self.tasks_layout.addWidget(empty_label)
            return

        for task in self.current_tasks:
            task_widget = self._create_task_card(task)
            self.tasks_layout.addWidget(task_widget)

    def _get_deadline_status(self, deadline_str):
        """Возвращает статус дедлайна для подсветки."""
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
        """Создаёт карточку задачи."""
        task_frame = QFrame()
        task_frame.setFrameShape(QFrame.Box)

        deadline_status = self._get_deadline_status(task.deadline)
        is_completed = task.status == "completed"

        # Стиль рамки в зависимости от статуса и срочности
        if is_completed:
            task_frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #4CAF50;
                    border-radius: 6px;
                    padding: 10px;
                    margin: 2px;
                    background-color: #e8f5e9;
                }
            """)
        elif deadline_status == "overdue":
            task_frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #ff4444;
                    border-radius: 6px;
                    padding: 10px;
                    margin: 2px;
                    background-color: #fff0f0;
                }
            """)
        elif deadline_status == "urgent":
            task_frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #ff8888;
                    border-radius: 6px;
                    padding: 10px;
                    margin: 2px;
                    background-color: #fff5f5;
                }
            """)
        elif deadline_status == "warning":
            task_frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #ffcc00;
                    border-radius: 6px;
                    padding: 10px;
                    margin: 2px;
                    background-color: #fffbe6;
                }
            """)
        else:
            task_frame.setStyleSheet("""
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

        layout = QVBoxLayout(task_frame)

        # ========== Верхняя строка ==========
        header_layout = QHBoxLayout()

        # Чекбокс
        checkbox = QCheckBox()
        checkbox.setChecked(is_completed)
        checkbox.stateChanged.connect(lambda state, tid=task.id: self._toggle_task_status(tid, state))
        header_layout.addWidget(checkbox)

        # Название
        title_label = QLabel(task.title)
        title_style = "font-size: 14px; font-weight: bold;"
        if is_completed:
            title_style += " text-decoration: line-through; color: #4CAF50;"
        title_label.setStyleSheet(title_style)
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label, stretch=1)

        # Дедлайн (только если не выполнена)
        if not is_completed and task.deadline:
            try:
                deadline_dt = datetime.fromisoformat(task.deadline)
                deadline_text = f"📅 {deadline_dt.strftime('%d.%m.%Y %H:%M')}"
                deadline_label = QLabel(deadline_text)

                if deadline_status == "overdue":
                    deadline_label.setStyleSheet("color: #ff4444; font-size: 11px; font-weight: bold;")
                elif deadline_status == "urgent":
                    deadline_label.setStyleSheet("color: #ff4444; font-size: 11px;")
                elif deadline_status == "warning":
                    deadline_label.setStyleSheet("color: #cc9900; font-size: 11px;")
                else:
                    deadline_label.setStyleSheet("color: #666; font-size: 11px;")

                header_layout.addWidget(deadline_label)
            except:
                pass

        # Если задача выполнена, показываем зелёную метку
        if is_completed:
            completed_label = QLabel("✅ Выполнена")
            completed_label.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: bold;")
            header_layout.addWidget(completed_label)

        # Кнопки
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(28, 28)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFC107;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #FFB300; }
        """)
        edit_btn.clicked.connect(lambda checked=False, tid=task.id: self.edit_task(tid))
        header_layout.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #D32F2F; }
        """)
        delete_btn.clicked.connect(lambda checked=False, tid=task.id: self.delete_task(tid))
        header_layout.addWidget(delete_btn)

        layout.addLayout(header_layout)

        # Описание (для всех задач)
        if task.description:
            desc_label = QLabel(task.description)
            desc_label.setWordWrap(True)
            if is_completed:
                desc_label.setStyleSheet("color: #888; font-size: 12px; margin-left: 25px;")
            else:
                desc_label.setStyleSheet("color: #555; font-size: 12px; margin-left: 25px;")
            layout.addWidget(desc_label)

        # Дата создания
        if task.created_at:
            try:
                created_dt = datetime.fromisoformat(task.created_at)
                created_label = QLabel(f"📝 Создана: {created_dt.strftime('%d.%m.%Y %H:%M')}")
                if is_completed:
                    created_label.setStyleSheet("color: #aaa; font-size: 10px; margin-left: 25px;")
                else:
                    created_label.setStyleSheet("color: #999; font-size: 10px; margin-left: 25px;")
                layout.addWidget(created_label)
            except:
                pass

        return task_frame

    def _toggle_task_status(self, task_id: int, state: int):
        """Переключает статус задачи."""
        status = "completed" if state == 2 else "active"
        self.task_controller.update_task_status(task_id, status)
        self.load_tasks()
        self.tasks_updated.emit()

    def create_task(self):
        """Создаёт новую задачу."""
        dialog = TaskDialog(self)

        if dialog.exec():
            title = dialog.get_title()
            if title:
                self.task_controller.create_task(
                    title=title,
                    description=dialog.get_description(),
                    topic_id=self.topic_id,
                    deadline=dialog.get_deadline()
                )
                self.load_tasks()
                self.tasks_updated.emit()
                QMessageBox.information(self, "Готово", f"Задача «{title}» создана!")

    def edit_task(self, task_id: int):
        """Редактирует задачу."""
        task = next((t for t in self.current_tasks if t.id == task_id), None)
        if not task:
            return

        dialog = TaskDialog(self)
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
                QMessageBox.information(self, "Готово", "Задача обновлена!")

    def delete_task(self, task_id: int):
        """Удаляет задачу."""
        reply = QMessageBox.question(
            self, "Удаление",
            "Вы уверены, что хотите удалить эту задачу?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.task_controller.delete_task(task_id)
            self.load_tasks()
            self.tasks_updated.emit()

    def refresh(self):
        """Обновляет список задач."""
        self.load_tasks()