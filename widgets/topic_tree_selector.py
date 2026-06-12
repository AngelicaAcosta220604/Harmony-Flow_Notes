# widgets/topic_tree_selector.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QCheckBox, QHeaderView
)
from PySide6.QtCore import Qt


class TopicTreeSelector(QWidget):
    """Дерево тем с чекбоксами для выбора"""

    def __init__(self, topic_controller, parent=None):
        super().__init__(parent)
        self.topic_controller = topic_controller
        self.all_topics = []
        self.checkboxes = {}  # храним чекбоксы по id темы

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(20)
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #DDD;
                border-radius: 6px;
                background-color: white;
            }
            QTreeWidget::item {
                padding: 4px;
            }
        """)

        layout.addWidget(self.tree)

        self.load_topics()

    def load_topics(self):
        """Загружает темы в дерево"""
        self.tree.clear()
        self.checkboxes.clear()
        self.all_topics = self.topic_controller.get_all_topics()

        print(f"DEBUG TopicTreeSelector: загружено {len(self.all_topics)} тем")

        if not self.all_topics:
            empty_item = QTreeWidgetItem()
            empty_item.setText(0, "📭 Нет тем. Создайте тему через раздел 'Темы'")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsSelectable)
            self.tree.addTopLevelItem(empty_item)
            return

        # Строим дерево
        items_map = {}

        # Сначала создаём все элементы
        for topic in self.all_topics:
            item = QTreeWidgetItem()
            item.setData(0, Qt.UserRole, topic.id)

            # Создаём текст с иконкой и названием (без чекбокса в тексте)
            icon = "📁" if topic.type == "folder" else "📄"
            item.setText(0, f"{icon} {topic.name}")

            items_map[topic.id] = item

        # Выстраиваем иерархию
        for topic in self.all_topics:
            item = items_map[topic.id]

            if topic.parent_id is None:
                self.tree.addTopLevelItem(item)
            else:
                parent_item = items_map.get(topic.parent_id)
                if parent_item:
                    parent_item.addChild(item)
                else:
                    self.tree.addTopLevelItem(item)

        # Добавляем чекбоксы ТОЛЬКО для тем (не для папок)
        for topic in self.all_topics:
            if topic.type == "topic":
                item = items_map[topic.id]
                # Создаём чекбокс
                checkbox = QCheckBox()
                checkbox.setEnabled(True)
                # Сохраняем чекбокс
                self.checkboxes[topic.id] = checkbox
                # Добавляем чекбокс в колонку 0 (рядом с текстом)
                self.tree.setItemWidget(item, 0, checkbox)

                # НЕ устанавливаем текст через setText, чтобы чекбокс не перекрывал
                # Вместо этого создаём отдельную колонку для текста
                # Но у нас только одна колонка, поэтому делаем так:
                # Убираем текст из item, он будет только в чекбоксе
                item.setText(0, "")  # очищаем текст
                checkbox.setText(f"{icon} {topic.name}")  # текст на чекбоксе

        self.tree.expandAll()

        print(f"DEBUG TopicTreeSelector: добавлено {len(items_map)} элементов, чекбоксов: {len(self.checkboxes)}")

    def get_selected_topic_ids(self) -> list:
        """Возвращает список ID выбранных тем"""
        selected_ids = []
        for topic_id, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                selected_ids.append(topic_id)
        return selected_ids

    def select_all(self):
        """Выбирает все темы"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)

    def clear_all(self):
        """Снимает все выделения"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)