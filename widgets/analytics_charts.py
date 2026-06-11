# widgets/analytics_charts.py

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class AnalyticsCharts(QWidget):
    """Виджет для отображения графиков matplotlib"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def clear(self):
        self.figure.clear()
        self.canvas.draw()

    def plot_trend(self, data, title="Динамика показателей"):
        """График тренда по сессиям"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not data:
            ax.text(0.5, 0.5, "Нет данных", ha='center', va='center')
            self.canvas.draw()
            return

        dates = [d['date'] for d in data]
        concentrations = [d['concentration'] for d in data]
        energies = [d['energy'] for d in data]
        interests = [d['interest'] for d in data]

        x = range(len(dates))
        ax.plot(x, concentrations, 'b-o', label='Концентрация', linewidth=2)
        ax.plot(x, energies, 'g-s', label='Энергия', linewidth=2)
        ax.plot(x, interests, 'r-^', label='Интерес', linewidth=2)

        ax.set_xlabel('Сессии')
        ax.set_ylabel('Уровень (1-5)')
        ax.set_title(title)
        ax.legend()
        ax.set_ylim(0, 5.5)
        ax.grid(True, alpha=0.3)

        # Подписи оси X
        if len(dates) <= 10:
            ax.set_xticks(x)
            ax.set_xticklabels(dates, rotation=45, ha='right', fontsize=8)
        else:
            step = len(dates) // 5
            ax.set_xticks(x[::step])
            ax.set_xticklabels(dates[::step], rotation=45, ha='right', fontsize=8)

        self.figure.tight_layout()
        self.canvas.draw()

    def plot_time_of_day(self, data, title="Продуктивность по часам"):
        """График по часам суток"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not data:
            ax.text(0.5, 0.5, "Нет данных", ha='center', va='center')
            self.canvas.draw()
            return

        hours = [d['hour'] for d in data]
        concentrations = [d['concentration'] for d in data]

        ax.bar(hours, concentrations, color='steelblue', width=0.8)
        ax.set_xlabel('Час суток')
        ax.set_ylabel('Средняя концентрация')
        ax.set_title(title)
        ax.set_xticks(range(0, 24, 2))
        ax.set_ylim(0, 5.5)
        ax.grid(True, alpha=0.3, axis='y')

        self.figure.tight_layout()
        self.canvas.draw()

    def plot_day_of_week(self, data, title="Продуктивность по дням недели"):
        """График по дням недели"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not data:
            ax.text(0.5, 0.5, "Нет данных", ha='center', va='center')
            self.canvas.draw()
            return

        days = [d['day'] for d in data]
        concentrations = [d['concentration'] for d in data]

        ax.bar(days, concentrations, color='steelblue', width=0.6)
        ax.set_xlabel('День недели')
        ax.set_ylabel('Средняя концентрация')
        ax.set_title(title)
        ax.set_ylim(0, 5.5)
        ax.grid(True, alpha=0.3, axis='y')

        self.figure.tight_layout()
        self.canvas.draw()

    def plot_duration(self, data, title="Концентрация vs Длительность"):
        """График зависимости концентрации от длительности"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not data:
            ax.text(0.5, 0.5, "Нет данных", ha='center', va='center')
            self.canvas.draw()
            return

        ranges = [d['range'] for d in data]
        concentrations = [d['avg_concentration'] for d in data]

        ax.bar(ranges, concentrations, color='steelblue', width=0.6)
        ax.set_xlabel('Длительность сессии (мин)')
        ax.set_ylabel('Средняя концентрация')
        ax.set_title(title)
        ax.set_ylim(0, 5.5)
        ax.grid(True, alpha=0.3, axis='y')

        self.figure.tight_layout()
        self.canvas.draw()

    def plot_session_minutes(self, minutes, concentration, energy, interest, title="Детали сессии"):
        """График по минутам сессии (3 кривые)"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not minutes:
            ax.text(0.5, 0.5, "Нет данных", ha='center', va='center')
            self.canvas.draw()
            return

        ax.plot(minutes, concentration, 'b-o', label='Концентрация', linewidth=2, markersize=4)
        ax.plot(minutes, energy, 'g-s', label='Энергия', linewidth=2, markersize=4)
        ax.plot(minutes, interest, 'r-^', label='Интерес', linewidth=2, markersize=4)

        ax.set_xlabel('Минута сессии')
        ax.set_ylabel('Уровень (1-5)')
        ax.set_title(title)
        ax.legend()
        ax.set_ylim(0, 5.5)
        ax.grid(True, alpha=0.3)

        self.figure.tight_layout()
        self.canvas.draw()