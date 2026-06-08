from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtGui import QPainter
from PySide6.QtCore import QPointF


class AnalyticsCharts(QWidget):
    """
    Прототип виджета аналитических графиков.
    Позже сюда можно подключить реальные данные из AnalyticsController.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # Заголовок (можно скрыть или заменить)
        self.title = QLabel("Графики аналитики")
        self.layout.addWidget(self.title)

        # Основной график
        self.chart = QChart()
        self.chart.setTitle("Пример графика (заглушка)")

        # Пример данных (заглушка)
        series = QLineSeries()
        series.append([QPointF(0, 1), QPointF(1, 3), QPointF(2, 2), QPointF(3, 5)])

        self.chart.addSeries(series)
        self.chart.createDefaultAxes()

        # Виджет отображения графика
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.layout.addWidget(self.chart_view)

    # ---------------------------------------------------------
    # Методы для обновления графиков
    # ---------------------------------------------------------

    def show_daily_chart(self, data):
        """
        data: список чисел или список (x, y)
        """
        self._update_chart("Статистика за день", data)

    def show_weekly_chart(self, data):
        self._update_chart("Статистика за неделю", data)

    def show_monthly_chart(self, data):
        self._update_chart("Статистика за месяц", data)

    # ---------------------------------------------------------
    # Внутренний метод обновления графика
    # ---------------------------------------------------------

    def _update_chart(self, title: str, data):
        self.chart.removeAllSeries()
        self.chart.setTitle(title)

        series = QLineSeries()

        # data может быть:
        # [1, 2, 3] → авто x
        # [(0,1), (1,2)] → пары
        if data and isinstance(data[0], (int, float)):
            for i, y in enumerate(data):
                series.append(i, y)
        else:
            for x, y in data:
                series.append(x, y)

        self.chart.addSeries(series)
        self.chart.createDefaultAxes()
