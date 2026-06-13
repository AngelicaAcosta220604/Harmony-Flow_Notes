# views/global_tasks_view.py

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget, QFrame, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt, Signal
from views.base_tasks_view import BaseTasksView
from widgets.task_dialog import TaskDialog
from widgets.silent_dialog import SilentMessageBox
from services import TimeService


class GlobalTasksView(BaseTasksView):
    """Глобальная вкладка задач - показывает задачи из ВСЕХ тем"""

    def __init__(self, task_controller, topic_controller, parent=None):
        self.topic_controller = topic_controller
        super().__init__(task_controller, parent)
        self._add_topic_filter()

    def _add_topic_filter(self):
        """Добавляет фильтр по теме в верхнюю панель"""
        # Находим top_bar в верхней панели
        top_panel = self.layout().itemAt(0).widget()
        if top_panel:
            top_layout = top_panel.layout()
            if top_layout and top_layout.count() > 0:
                top_bar = top_layout.itemAt(0).layout()
                if top_bar:
                    # Добавляем разделитель
                    spacer = QWidget()
                    spacer.setFixedWidth(20)
                    top_bar.insertWidget(3, spacer)

                    # Добавляем фильтр по теме
                    topic_label = QLabel("Тема:")
                    topic_label.setStyleSheet("font-size: 12px;")
                    top_bar.insertWidget(4, topic_label)

                    self.topic_filter = QComboBox()
                    self.topic_filter.addItem("📚 Все темы", None)
                    # Загружаем темы
                    topics = self.topic_controller.get_all_topics()
                    for topic in topics:
                        if topic.type == "topic":
                            self.topic_filter.addItem(f"📄 {topic.name}", topic.id)
                    self.topic_filter.setMinimumWidth(180)
                    self.topic_filter.setStyleSheet("""
                        QComboBox {
                            padding: 4px 8px;
                            border: 1px solid #CCC;
                            border-radius: 4px;
                            background-color: white;
                            font-size: 12px;
                        }
                    """)
                    self.topic_filter.currentIndexChanged.connect(self.load_tasks)
                    top_bar.insertWidget(5, self.topic_filter)

    def get_tasks(self):
        """Возвращает все задачи из всех тем"""
        all_tasks = self.task_controller.get_all_tasks()

        # Фильтруем по теме, если выбран конкретная тема
        if hasattr(self, 'topic_filter') and self.topic_filter:
            selected_topic_id = self.topic_filter.currentData()
            if selected_topic_id:
                all_tasks = [t for t in all_tasks if t.topic_id == selected_topic_id]

        return all_tasks

    def create_task(self):
        """Создаёт новую задачу с выбором темы"""
        dialog = TaskDialog(self)
        dialog.setMinimumWidth(450)

        # Добавляем выбор темы в диалог
        from PySide6.QtWidgets import QComboBox, QLabel

        # Находим layout диалога
        layout = dialog.layout()

        # Создаем контейнер для темы
        topic_widget = QWidget()
        topic_layout = QHBoxLayout(topic_widget)
        topic_layout.setContentsMargins(0, 0, 0, 0)

        topic_label = QLabel("Тема:")
        topic_label.setMinimumWidth(40)
        topic_layout.addWidget(topic_label)

        topic_combo = QComboBox()
        # Загружаем темы
        topics = self.topic_controller.get_all_topics()
        for topic in topics:
            if topic.type == "topic":
                topic_combo.addItem(f"📄 {topic.name}", topic.id)
        topic_combo.setMinimumWidth(200)
        topic_layout.addWidget(topic_combo)
        topic_layout.addStretch()

        # Вставляем после заголовка окна
        layout.insertWidget(0, topic_widget)

        # Сохраняем ссылку на комбобокс в диалоге
        dialog.topic_combo = topic_combo

        if dialog.exec():
            title = dialog.get_title()
            if title:
                topic_id = dialog.topic_combo.currentData()
                self.task_controller.create_task(
                    title=title,
                    description=dialog.get_description(),
                    topic_id=topic_id,
                    deadline=dialog.get_deadline()
                )
                self.load_tasks()
                self.tasks_updated.emit()
                self.task_added.emit(None)
                SilentMessageBox.information(self, "Готово", f"Задача «{title}» создана!")

    def _create_task_card(self, task):
        """Переопределяем создание карточки, чтобы показывать название темы"""
        task_frame = super()._create_task_card(task)

        # Добавляем название темы в карточку
        topic = self.topic_controller.get_topic(task.topic_id)
        if topic:
            # Находим layout и header_layout
            layout = task_frame.layout()
            if layout and layout.count() > 0:
                header_layout = layout.itemAt(0).layout()
                if header_layout:
                    # Проверяем, есть ли уже метка темы
                    existing = header_layout.itemAt(0)
                    if existing and existing.widget() and "topic_label" in str(existing.widget().objectName()):
                        pass
                    else:
                        topic_label = QLabel(f"📁 {topic.name}")
                        topic_label.setObjectName("topic_label")
                        topic_label.setStyleSheet(
                            "color: #666; font-size: 10px; padding: 2px 6px; background-color: #f0f0f0; border-radius: 4px;")
                        header_layout.insertWidget(0, topic_label)

        return task_frame