from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from .base_view import BaseView


class SearchView(BaseView):
    """
    Экран глобального поиска.
    Содержит:
    - строку поиска (вынесена в SearchBarWidget)
    - список результатов
    """

    def __init__(self, search_controller, parent=None):
        super().__init__(parent)

        self.search_controller = search_controller

        # Заголовок
        self.title = QLabel("Поиск")
        self.layout.addWidget(self.title)

        # Список результатов
        self.results_list = QListWidget()
        self.layout.addWidget(self.results_list)

    def show_results(self, results: list):
        """
        Обновляет список результатов поиска.
        results — список словарей:
            {
                'type': 'note' | 'task' | 'flashcard' | 'topic',
                'title': str,
                'snippet': str
            }
        """
        self.results_list.clear()

        for item in results:
            text = f"[{item['type']}] {item['title']}\n{item.get('snippet', '')}"
            QListWidgetItem(text, self.results_list)

    def refresh(self):
        """Обновление экрана (если нужно)."""
        pass
