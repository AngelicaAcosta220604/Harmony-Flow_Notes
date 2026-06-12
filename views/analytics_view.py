# views/analytics_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QComboBox, QDateEdit
)
from PySide6.QtCore import Qt, Signal, QDate
from datetime import datetime, timedelta
import matplotlib
from widgets.silent_message_box import QMessageBox
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class AnalyticsView(QWidget):
    """Виджет для отображения аналитики (общей или по теме)"""

    def __init__(self, analytics_controller=None, is_topic_view=False, parent=None):
        super().__init__(parent)
        self.analytics_controller = analytics_controller
        self.is_topic_view = is_topic_view  # True = аналитика внутри темы, False = глобальная
        self.current_period = "week"  # day, week, month, all
        self.current_date = QDate.currentDate()

        self.setup_ui()
        if self.analytics_controller:
            self.load_data()

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)

        # ========== Панель управления ==========
        control_bar = QHBoxLayout()

        # Выбор периода
        control_bar.addWidget(QLabel("Период:"))
        self.period_combo = QComboBox()
        self.period_combo.addItem("День", "day")
        self.period_combo.addItem("Неделя", "week")
        self.period_combo.addItem("Месяц", "month")
        self.period_combo.addItem("Всё время", "all")
        self.period_combo.setCurrentIndex(1)  # неделя по умолчанию
        self.period_combo.currentIndexChanged.connect(self._on_period_changed)
        control_bar.addWidget(self.period_combo)

        control_bar.addSpacing(20)

        # Выбор даты
        control_bar.addWidget(QLabel("Дата:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        self.date_edit.dateChanged.connect(self._on_date_changed)
        control_bar.addWidget(self.date_edit)

        control_bar.addStretch()

        # Кнопка обновления
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.clicked.connect(self.load_data)
        control_bar.addWidget(self.refresh_btn)

        layout.addLayout(control_bar)

        # ========== Область с графиками и статистикой ==========
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setSpacing(15)

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

    def _on_period_changed(self):
        self.current_period = self.period_combo.currentData()
        self.load_data()

    def _on_date_changed(self, date: QDate):
        self.current_date = date
        self.load_data()

    def _get_date_range(self):
        """Возвращает начальную и конечную дату для выбранного периода"""
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

    def load_data(self):
        """Загружает и отображает аналитику"""
        if not self.analytics_controller:
            return

        # Очищаем контейнер
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            # Получаем сессии за период
            start_date, end_date = self._get_date_range()

            if start_date and end_date:
                start_dt = datetime(start_date.year(), start_date.month(), start_date.day())
                end_dt = datetime(end_date.year(), end_date.month(), end_date.day(), 23, 59, 59)
            else:
                start_dt = None
                end_dt = None

            # Для аналитики по теме используем topic_sessions, иначе все сессии
            if hasattr(self.analytics_controller, 'get_topic_sessions'):
                sessions = self.analytics_controller.get_topic_sessions()
            else:
                sessions = self.analytics_controller.get_sessions_in_range(start_dt, end_dt)

            # Получаем статистику
            stats = self.analytics_controller.get_session_stats(sessions)
            insights = self.analytics_controller.generate_insights(sessions)

            # Отображаем статистику
            self._display_stats(stats)

            # Отображаем графики
            self._display_charts(sessions)

            # Отображаем выводы
            self._display_insights(insights)

        except Exception as e:
            error_label = QLabel(f"Ошибка загрузки данных: {str(e)}")
            error_label.setStyleSheet("color: red; padding: 20px;")
            self.content_layout.addWidget(error_label)

    def _display_stats(self, stats: dict):
        """Отображает статистику в виде карточек"""
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layout = QVBoxLayout(stats_frame)

        title = QLabel("📊 Общая статистика")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Сетка 2x2
        grid_layout = QHBoxLayout()

        # Карточка 1: Сессии
        card1 = QFrame()
        card1.setStyleSheet("background-color: white; border-radius: 6px; padding: 10px;")
        card1_layout = QVBoxLayout(card1)
        card1_layout.addWidget(QLabel("⏱ Сессии"))
        card1_layout.addWidget(QLabel(f"{stats['total_sessions']}"))
        card1_layout.addWidget(QLabel(f"{stats['total_hours']} часов"))
        grid_layout.addWidget(card1)

        # Карточка 2: Средняя концентрация
        card2 = QFrame()
        card2.setStyleSheet("background-color: white; border-radius: 6px; padding: 10px;")
        card2_layout = QVBoxLayout(card2)
        card2_layout.addWidget(QLabel("🧠 Концентрация"))
        card2_layout.addWidget(QLabel(f"{stats['avg_concentration']}/5"))
        card2_layout.addWidget(QLabel(f"Средняя"))
        grid_layout.addWidget(card2)

        # Карточка 3: Энергия
        card3 = QFrame()
        card3.setStyleSheet("background-color: white; border-radius: 6px; padding: 10px;")
        card3_layout = QVBoxLayout(card3)
        card3_layout.addWidget(QLabel("⚡ Энергия"))
        card3_layout.addWidget(QLabel(f"{stats['avg_energy']}/5"))
        card3_layout.addWidget(QLabel(f"Средняя"))
        grid_layout.addWidget(card3)

        # Карточка 4: Интерес
        card4 = QFrame()
        card4.setStyleSheet("background-color: white; border-radius: 6px; padding: 10px;")
        card4_layout = QVBoxLayout(card4)
        card4_layout.addWidget(QLabel("❤️ Интерес"))
        card4_layout.addWidget(QLabel(f"{stats['avg_interest']}/5"))
        card4_layout.addWidget(QLabel(f"Средний"))
        grid_layout.addWidget(card4)

        layout.addLayout(grid_layout)

        # Дополнительная информация
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"📅 Первая сессия: {stats['first_session']}"))
        info_layout.addWidget(QLabel(f"📅 Последняя сессия: {stats['last_session']}"))
        info_layout.addStretch()
        layout.addLayout(info_layout)

        self.content_layout.addWidget(stats_frame)

    def _display_charts(self, sessions):
        """Отображает графики"""
        if len(sessions) < 2:
            chart_frame = QFrame()
            chart_frame.setStyleSheet("background-color: #F5F5F5; border-radius: 8px; padding: 15px;")
            layout = QVBoxLayout(chart_frame)
            layout.addWidget(QLabel("📈 График динамики"))
            layout.addWidget(QLabel("Недостаточно данных для построения графика. Проведите больше сессий."))
            self.content_layout.addWidget(chart_frame)
            return

        # Создаём график
        figure = Figure(figsize=(8, 4), dpi=100)
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111)

        # Получаем данные
        dates, conc_values = self.analytics_controller.get_session_timeline(sessions, "concentration")
        _, energy_values = self.analytics_controller.get_session_timeline(sessions, "energy")
        _, interest_values = self.analytics_controller.get_session_timeline(sessions, "interest")

        # Ограничиваем количество точек
        max_points = 20
        if len(dates) > max_points:
            step = len(dates) // max_points
            dates = dates[::step]
            conc_values = conc_values[::step]
            energy_values = energy_values[::step]
            interest_values = interest_values[::step]

        ax.plot(dates, conc_values, 'b-o', label='Концентрация', linewidth=2, markersize=6)
        ax.plot(dates, energy_values, 'g-s', label='Энергия', linewidth=2, markersize=6)
        ax.plot(dates, interest_values, 'r-^', label='Интерес', linewidth=2, markersize=6)

        ax.set_ylim(0, 5.5)
        ax.set_ylabel('Оценка (1-5)')
        ax.set_xlabel('Дата сессии')
        ax.set_title('Динамика показателей')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)

        figure.tight_layout()

        chart_frame = QFrame()
        chart_frame.setStyleSheet("background-color: #F5F5F5; border-radius: 8px; padding: 15px;")
        layout = QVBoxLayout(chart_frame)
        layout.addWidget(QLabel("📈 Динамика показателей по сессиям"))
        layout.addWidget(canvas)

        self.content_layout.addWidget(chart_frame)

    def _display_insights(self, insights: list):
        """Отображает текстовые выводы"""
        insights_frame = QFrame()
        insights_frame.setStyleSheet("""
            QFrame {
                background-color: #E8F4F8;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #51b2c1;
            }
        """)
        layout = QVBoxLayout(insights_frame)

        layout.addWidget(QLabel("💡 Аналитика и советы"))
        layout.addWidget(QLabel("─" * 40))

        for insight in insights:
            insight_label = QLabel(f"• {insight}")
            insight_label.setWordWrap(True)
            insight_label.setStyleSheet("margin-left: 10px; margin-bottom: 5px;")
            layout.addWidget(insight_label)

        self.content_layout.addWidget(insights_frame)

    def load_session_analytics(self, session_id: int):
        """Загружает аналитику по конкретной сессии"""
        if not self.analytics_controller or not hasattr(self.analytics_controller, 'get_session_analytics'):
            return

        data = self.analytics_controller.get_session_analytics(session_id)
        if "error" in data:
            return

        # Очищаем контейнер
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        session = data["session"]
        stats = data["averages"]
        peaks = data["peaks"]
        graph_data = data["graph_data"]
        insights = data["insights"]

        # ========== Информация о сессии ==========
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #F5F5F5; border-radius: 8px; padding: 15px;")
        info_layout = QVBoxLayout(info_frame)

        date_str = datetime.fromisoformat(session.start_time).strftime("%d.%m.%Y %H:%M") if session.start_time else "—"
        info_layout.addWidget(QLabel(f"📅 Сессия от {date_str}"))
        info_layout.addWidget(QLabel(
            f"⏱ Длительность: {session.duration_minutes} минут" if session.duration_minutes else "⏱ Длительность: —"))

        self.content_layout.addWidget(info_frame)

        # ========== Показатели ==========
        metrics_frame = QFrame()
        metrics_frame.setStyleSheet("background-color: #F5F5F5; border-radius: 8px; padding: 15px;")
        metrics_layout = QHBoxLayout(metrics_frame)

        metrics_layout.addWidget(
            QLabel(f"🧠 Концентрация: средняя {stats['concentration']:.1f} / макс {peaks['concentration']}/5"))
        metrics_layout.addWidget(QLabel(f"⚡ Энергия: средняя {stats['energy']:.1f} / макс {peaks['energy']}/5"))
        metrics_layout.addWidget(QLabel(f"❤️ Интерес: средний {stats['interest']:.1f} / макс {peaks['interest']}/5"))
        metrics_layout.addStretch()

        self.content_layout.addWidget(metrics_frame)

        # ========== График по минутам ==========
        if graph_data["minutes"] and len(graph_data["minutes"]) > 1:
            figure = Figure(figsize=(8, 4), dpi=100)
            canvas = FigureCanvas(figure)
            ax = figure.add_subplot(111)

            ax.plot(graph_data["minutes"], graph_data["concentration"], 'b-o', label='Концентрация', linewidth=2,
                    markersize=4)
            ax.plot(graph_data["minutes"], graph_data["energy"], 'g-s', label='Энергия', linewidth=2, markersize=4)
            ax.plot(graph_data["minutes"], graph_data["interest"], 'r-^', label='Интерес', linewidth=2, markersize=4)

            ax.set_ylim(0, 5.5)
            ax.set_xlabel('Минута сессии')
            ax.set_ylabel('Оценка (1-5)')
            ax.set_title('Динамика показателей по минутам')
            ax.legend(loc='upper right')
            ax.grid(True, alpha=0.3)

            figure.tight_layout()

            chart_frame = QFrame()
            chart_frame.setStyleSheet("background-color: #F5F5F5; border-radius: 8px; padding: 15px;")
            chart_layout = QVBoxLayout(chart_frame)
            chart_layout.addWidget(QLabel("📈 Динамика сессии по минутам"))
            chart_layout.addWidget(canvas)
            self.content_layout.addWidget(chart_frame)

        # ========== Выводы ==========
        insights_frame = QFrame()
        insights_frame.setStyleSheet(
            "background-color: #E8F4F8; border-radius: 8px; padding: 15px; border: 1px solid #51b2c1;")
        insights_layout = QVBoxLayout(insights_frame)
        insights_layout.addWidget(QLabel("💡 Анализ сессии:"))

        for insight in insights:
            label = QLabel(f"• {insight}")
            label.setWordWrap(True)
            insights_layout.addWidget(label)

        self.content_layout.addWidget(insights_frame)

    def refresh(self):
        """Обновляет данные"""
        self.load_data()