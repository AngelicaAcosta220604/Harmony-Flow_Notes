# widgets/tree_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QPushButton,
    QMenu, QInputDialog, QMessageBox
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QPoint, Signal
from controllers.topic_controller import TopicController


class TreeWidget(QWidget):
    topic_selected = Signal(int)  # сигнал при выборе темы (передаём topic_id)

    def __init__(self, topic_controller: TopicController, parent=None):
        super().__init__(parent)
        self.topic_controller = topic_controller
        self.current_parent_id = None  # для хранения выбранной папки

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # Дерево
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._open_context_menu)
        self.tree.itemClicked.connect(self._on_item_clicked)

        self.layout.addWidget(self.tree)

        # Нижняя панель кнопок
        btn_row = QHBoxLayout()
        self.btn_new_folder = QPushButton("+ Новая папка")
        self.btn_new_topic = QPushButton("+ Новая тема")
        btn_row.addWidget(self.btn_new_folder)
        btn_row.addWidget(self.btn_new_topic)
        self.layout.addLayout(btn_row)

        # Подключаем кнопки
        self.btn_new_folder.clicked.connect(self._create_folder)
        self.btn_new_topic.clicked.connect(self._create_topic)

    # ---------------------------------------------------------
    # ЗАГРУЗКА ДАННЫХ ИЗ БД
    # ---------------------------------------------------------
    def load_topics(self):
        """Загружает все темы из БД и строит дерево."""
        self.tree.clear()
        topics = self.topic_controller.get_all_topics()

        items_map = {}

        # Создаём все элементы
        for topic in topics:
            item = QTreeWidgetItem()
            icon = "📁" if topic.type == "folder" else "📄"
            item.setText(0, f"{icon} {topic.name}")
            item.setData(0, Qt.UserRole, topic.id)
            items_map[topic.id] = item

        # Расставляем родителей
        for topic in topics:
            item = items_map[topic.id]
            if topic.parent_id is None:
                self.tree.addTopLevelItem(item)
            else:
                parent_item = items_map.get(topic.parent_id)
                if parent_item:
                    parent_item.addChild(item)

        self.tree.expandAll()

    # ---------------------------------------------------------
    # ОПЕРАЦИИ С ТЕМАМИ
    # ---------------------------------------------------------
    def _get_selected_topic_id(self):
        """Возвращает id выбранной темы/папки или None."""
        item = self.tree.currentItem()
        if item:
            return item.data(0, Qt.UserRole)
        return None

    def _get_selected_item(self):
        return self.tree.currentItem()

    def _create_folder(self):
        name, ok = QInputDialog.getText(self, "Новая папка", "Введите название папки:")
        if ok and name.strip():
            parent_id = self._get_selected_topic_id() if self._get_selected_item() else None
            self.topic_controller.add_topic(name.strip(), parent_id=parent_id, type="folder")
            self.load_topics()

    def _create_topic(self):
        name, ok = QInputDialog.getText(self, "Новая тема", "Введите название темы:")
        if ok and name.strip():
            parent_id = self._get_selected_topic_id() if self._get_selected_item() else None
            self.topic_controller.add_topic(name.strip(), parent_id=parent_id, type="topic")
            self.load_topics()

    def _rename_item(self, item: QTreeWidgetItem):
        topic_id = item.data(0, Qt.UserRole)
        if not topic_id:
            return
        old_name = item.text(0).split(" ", 1)[-1]
        new_name, ok = QInputDialog.getText(self, "Переименовать", "Новое название:", text=old_name)
        if ok and new_name.strip():
            self.topic_controller.rename_topic(topic_id, new_name.strip())
            self.load_topics()

    def _delete_item(self, item: QTreeWidgetItem):
        topic_id = item.data(0, Qt.UserRole)
        if not topic_id:
            return
        reply = QMessageBox.question(
            self, "Удаление",
            f"Удалить «{item.text(0)}» и всё содержимое?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.topic_controller.delete_topic(topic_id)
            self.load_topics()

    def _move_item(self, item: QTreeWidgetItem):
        """Перемещает выбранную тему/папку в другую папку."""
        topic_id = item.data(0, Qt.UserRole)
        if not topic_id:
            return

        # Получаем все папки для выбора
        all_topics = self.topic_controller.get_all_topics()
        folders = [t for t in all_topics if t.type == "folder" and t.id != topic_id]

        if not folders:
            QMessageBox.information(self, "Перемещение", "Нет доступных папок для перемещения.")
            return

        # Создаём список названий папок
        folder_names = [f"📁 {t.name}" for t in folders]
        folder_names.insert(0, "📁 Корень (без папки)")

        # Диалог выбора
        folder_name, ok = QInputDialog.getItem(
            self, "Переместить",
            "Выберите папку назначения:",
            folder_names, 0, False
        )
        if ok and folder_name:
            if folder_name == "📁 Корень (без папки)":
                new_parent_id = None
            else:
                # Находим id выбранной папки
                idx = folder_names.index(folder_name) - 1
                new_parent_id = folders[idx].id if idx >= 0 else None
            self.topic_controller.move_topic(topic_id, new_parent_id)
            self.load_topics()

    # ---------------------------------------------------------
    # КОНТЕКСТНОЕ МЕНЮ
    # ---------------------------------------------------------
    def _open_context_menu(self, pos: QPoint):
        item = self.tree.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        rename_action = QAction("Переименовать", self)
        delete_action = QAction("Удалить", self)
        move_action = QAction("Переместить", self)
        menu.addAction(rename_action)
        menu.addAction(delete_action)
        menu.addAction(move_action)
        rename_action.triggered.connect(lambda: self._rename_item(item))
        delete_action.triggered.connect(lambda: self._delete_item(item))
        move_action.triggered.connect(lambda: self._move_item(item))
        menu.exec(self.tree.mapToGlobal(pos))

    # ---------------------------------------------------------
    # ОБРАБОТКА ВЫБОРА ТЕМЫ
    # ---------------------------------------------------------
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        topic_id = item.data(0, Qt.UserRole)
        if topic_id:
            # Находим тип темы
            topic = self.topic_controller.get_topic(topic_id)
            if topic and topic.type == "topic":
                # Только темы отправляют сигнал (папки — нет)
                self.topic_selected.emit(topic_id)