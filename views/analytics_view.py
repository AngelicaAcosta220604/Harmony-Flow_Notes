# views/analytics_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QDateEdit, QFrame, QScrollArea,
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QDate, QDateTime
from controllers.analytics_controller import AnalyticsController
from widgets.analytics_charts import AnalyticsCharts
from datetime import datetime, timedelta


class AnalyticsView(QWidget):
    """Главный виджет аналитики"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.analytics_controller = AnalyticsController()

        self.current_start_date = None
        self.current_end_date = None
        self.current_period = "all"  # all, day, week, month, year

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Настройка интерфейса"""
        main_layout = QVBoxLayout(self)

        # ========== Панель фильтров ==========
        filter_bar = QHBoxLayout()

        # Выбор периода
        filter_bar.addWidget(QLabel("Период:"))
        self.period_combo = QComboBox()
        self.period_combo.addItem("📅 За всё время", "all")
        self.period_combo.addItem("📆 День", "day")
        self.period_combo.addItem("📆 Неделя", "week")
        self.period_combo.addItem("📆 Месяц", "month")
        self.period_combo.addItem("📆 Год", "year")
        self.period_combo.currentIndexChanged.connect(self._on_period_changed)
        filter_bar.addWidget(self.period_combo)

        filter_bar.addSpacing(20)

        # Дата начала
        filter_bar.addWidget(QLabel("С:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setDisplayFormat("dd.MM.yyyy")
        self.start_date.dateChanged.connect(self._on_date_range_changed)
        filter_bar.addWidget(self.start_date)

        # Дата конца
        filter_bar.addWidget(QLabel("По:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setDisplayFormat("dd.MM.yyyy")
        self.end_date.dateChanged.connect(self._on_date_range_changed)
        filter_bar.addWidget(self.end_date)

        filter_bar.addStretch()

        # Кнопка обновления
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.clicked.connect(self.load_data)
        filter_bar.addWidget(self.refresh_btn)

        main_layout.addLayout(filter_bar)

        # ========== Область с прокруткой ==========
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)

        # ----- Карточки с цифрами (4 в ряд) -----
        self.stats_widget = QWidget()
        self.stats_layout = QHBoxLayout(self.stats_widget)
        self.stats_layout.setSpacing(15)
        content_layout.addWidget(self.stats_widget)

        # ----- График тренда -----
        self.trend_chart = AnalyticsCharts()
        content_layout.addWidget(self.trend_chart)

        # ----- Анализ по времени и дням (2 колонки) -----
        time_day_layout = QHBoxLayout()

        # График по часам
        time_frame = QFrame()
        time_frame.setFrameShape(QFrame.Box)
        time_frame.setStyleSheet("border: 1px solid #DDD; border-radius: 6px;")
        time_layout = QVBoxLayout(time_frame)
        time_layout.addWidget(QLabel("⏰ Продуктивность по часам"))
        self.time_chart = AnalyticsCharts()
        time_layout.addWidget(self.time_chart)
        time_day_layout.addWidget(time_frame)

        # График по дням недели
        day_frame = QFrame()
        day_frame.setFrameShape(QFrame.Box)
        day_frame.setStyleSheet("border: 1px solid #DDD; border-radius: 6px;")
        day_layout = QVBoxLayout(day_frame)
        day_layout.addWidget(QLabel("📅 Продуктивность по дням"))
        self.day_chart = AnalyticsCharts()
        day_layout.addWidget(self.day_chart)
        time_day_layout.addWidget(day_frame)

        content_layout.addLayout(time_day_layout)

        # ----- Анализ длительности и топ тем (2 колонки) -----
        duration_topics_layout = QHBoxLayout()

        # График длительности
        duration_frame = QFrame()
        duration_frame.setFrameShape(QFrame.Box)
        duration_frame.setStyleSheet("border: 1px solid #DDD; border-radius: 6px;")
        duration_layout = QVBoxLayout(duration_frame)
        duration_layout.addWidget(QLabel("⏱ Концентрация vs Длительность"))
        self.duration_chart = AnalyticsCharts()
        duration_layout.addWidget(self.duration_chart)
        duration_topics_layout.addWidget(duration_frame)

        # Таблица топ тем
        topics_frame = QFrame()
        topics_frame.setFrameShape(QFrame.Box)
        topics_frame.setStyleSheet("border: 1px solid #DDD; border-radius: 6px;")
        topics_layout = QVBoxLayout(topics_frame)
        topics_layout.addWidget(QLabel("🏆 Топ тем по времени"))
        self.topics_table = QTableWidget()
        self.topics_table.setColumnCount(3)
        self.topics_table.setHorizontalHeaderLabels(["Тема", "Время", "Концентрация"])
        self.topics_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.topics_table.setAlternatingRowColors(True)
        topics_layout.addWidget(self.topics_table)
        duration_topics_layout.addWidget(topics_frame)

        content_layout.addLayout(duration_topics_layout)

        # ----- Таблица задач по темам -----
        tasks_frame = QFrame()
        tasks_frame.setFrameShape(QFrame.Box)
        tasks_frame.setStyleSheet("border: 1px solid #DDD; border-radius: 6px;")
        tasks_layout = QVBoxLayout(tasks_frame)
        tasks_layout.addWidget(QLabel("✅ Выполнение задач по темам"))
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(4)
        self.tasks_table.setHorizontalHeaderLabels(["Тема", "Всего", "Выполнено", "%"])
        self.tasks_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tasks_table.setAlternatingRowColors(True)
        tasks_layout.addWidget(self.tasks_table)
        content_layout.addWidget(tasks_frame)

        # ----- Текстовые выводы -----
        insights_frame = QFrame()
        insights_frame.setFrameShape(QFrame.Box)
        insights_frame.setStyleSheet("border: 1px solid #DDD; border-radius: 6px; background-color: #F5F5F5;")
        insights_layout = QVBoxLayout(insights_frame)
        insights_layout.addWidget(QLabel("💡 Автоматические выводы и советы"))
        self.insights_label = QLabel()
        self.insights_label.setWordWrap(True)
        self.insights_label.setStyleSheet("padding: 10px;")
        insights_layout.addWidget(self.insights_label)
        content_layout.addWidget(insights_frame)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _on_period_changed(self):
        """Обработчик смены периода"""
        period = self.period_combo.currentData()
        today = QDate.currentDate()

        if period == "day":
            self.start_date.setDate(today)
            self.end_date.setDate(today)
        elif period == "week":
            self.start_date.setDate(today.addDays(-7))
            self.end_date.setDate(today)
        elif period == "month":
            self.start_date.setDate(today.addDays(-30))
            self.end_date.setDate(today)
        elif period == "year":
            self.start_date.setDate(today.addDays(-365))
            self.end_date.setDate(today)
        else:
            self.start_date.setDate(QDate(2024, 1, 1))
            self.end_date.setDate(today)

        self.load_data()

    def _on_date_range_changed(self):
        """Обработчик изменения дат"""
        self.period_combo.setCurrentIndex(0)  # "За всё время"
        self.load_data()

    def load_data(self):
        """Загружает и отображает аналитику"""
        start_date = self.start_date.date().toPython()
        end_date = self.end_date.date().toPython()

        # Общая статистика
        stats = self.analytics_controller.get_general_stats(start_date, end_date)

        # Обновляем карточки
        self._update_stats_cards(stats)

        # График тренда
        trend = self.analytics_controller.get_session_trend(start_date, end_date)
        self.trend_chart.plot_trend(trend, "Динамика показателей по сессиям")

        # Анализ по часам
        time_data = self.analytics_controller.get_time_of_day_analytics(start_date, end_date)
        self.time_chart.plot_time_of_day(time_data)

        # Анализ по дням недели
        day_data = self.analytics_controller.get_day_of_week_analytics(start_date, end_date)
        self.day_chart.plot_day_of_week(day_data)

        # Анализ длительности
        duration_data = self.analytics_controller.get_duration_analytics(start_date, end_date)
        self.duration_chart.plot_duration(duration_data)

        # Топ тем
        topics = self.analytics_controller.get_topics_ranking(start_date, end_date)
        self._update_topics_table(topics)

        # Задачи по темам
        tasks_stats = self.analytics_controller.get_tasks_by_topic_stats(start_date, end_date)
        self._update_tasks_table(tasks_stats)

        # Текстовые выводы
        insights = self.analytics_controller.generate_insights(start_date, end_date)
        self._update_insights(insights)

    def _update_stats_cards(self, stats):
        """Обновляет карточки с цифрами"""
        # Очищаем
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cards = [
            ("⏱ Сессии", str(stats["sessions_count"])),
            ("🕐 Время", f"{stats['total_time_hours']}ч {stats['total_time_minutes']}м"),
            ("🧠 Концентрация", f"{stats['avg_concentration']}/5"),
            ("⚡ Энергия", f"{stats['avg_energy']}/5"),
            ("❤️ Интерес", f"{stats['avg_interest']}/5"),
            ("📝 Заметки", str(stats["notes_count"])),
            ("🃏 Карточки", str(stats["flashcards_count"])),
            ("✅ Задачи", f"{stats['completed_tasks']}/{stats['tasks_count']} ({stats['completion_rate']}%)")
        ]

        for title, value in cards:
            card = self._create_stat_card(title, value)
            self.stats_layout.addWidget(card)

    def _create_stat_card(self, title, value):
        """Создаёт карточку статистики"""
        card = QFrame()
        card.setFrameShape(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                border: 1px solid #DDD;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C3E50;")
        layout.addWidget(value_label)

        return card

    def _update_topics_table(self, topics):
        """Обновляет таблицу топ тем"""
        self.topics_table.setRowCount(len(topics))

        for row, topic in enumerate(topics):
            self.topics_table.setItem(row, 0, QTableWidgetItem(topic["name"]))

            hours = topic["time"] // 60
            minutes = topic["time"] % 60
            time_text = f"{hours}ч {minutes}м"
            self.topics_table.setItem(row, 1, QTableWidgetItem(time_text))

            self.topics_table.setItem(row, 2, QTableWidgetItem(f"{topic['avg_concentration']}/5"))

    def _update_tasks_table(self, tasks_stats):
        """Обновляет таблицу задач по темам"""
        self.tasks_table.setRowCount(len(tasks_stats))

        for row, task in enumerate(tasks_stats):
            self.tasks_table.setItem(row, 0, QTableWidgetItem(task["name"]))
            self.tasks_table.setItem(row, 1, QTableWidgetItem(str(task["total"])))
            self.tasks_table.setItem(row, 2, QTableWidgetItem(str(task["completed"])))

            percent_item = QTableWidgetItem(f"{task['completed_percent']}%")
            if task['completed_percent'] >= 80:
                percent_item.setForeground(Qt.darkGreen)
            elif task['completed_percent'] >= 50:
                percent_item.setForeground(Qt.darkYellow)
            else:
                percent_item.setForeground(Qt.red)
            self.tasks_table.setItem(row, 3, percent_item)

    def _update_insights(self, insights):
        """Обновляет текстовые выводы"""
        if not insights:
            self.insights_label.setText("Нет данных для анализа")
            return

        text = "• " + "\n• ".join(insights)
        self.insights_label.setText(text)

    def refresh(self):
        """Обновляет аналитику"""
        self.load_data()