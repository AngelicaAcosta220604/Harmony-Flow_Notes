# widgets/tree_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QPushButton,
    QMenu, QInputDialog, QMessageBox, QLineEdit
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QPoint, Signal
from controllers.topic_controller import TopicController


class TreeWidget(QWidget):
    topic_selected = Signal(int)

    def __init__(self, topic_controller: TopicController, parent=None):
        super().__init__(parent)
        self.topic_controller = topic_controller
        self.all_topics = []

        # Главный лэйаут с отступами
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # ← отступы со всех сторон
        layout.setSpacing(10)  # ← расстояние между элементами

        # ========== Строка поиска ==========
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск по темам...")
        self.search_input.setMinimumHeight(32)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 6px 10px;
                border: 1px solid #CCC;
                border-radius: 6px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2C3E50;
            }
        """)
        self.search_input.textChanged.connect(self._filter_topics)
        layout.addWidget(self.search_input)

        # ========== Кнопки добавления папки/темы ==========
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)  # расстояние между кнопками

        self.btn_new_folder = QPushButton("📁 Новая папка")
        self.btn_new_topic = QPushButton("📄 Новая тема")

        btn_style = """
            QPushButton {
                padding: 6px 12px;
                background-color: #F0F0F0;
                border: 1px solid #CCC;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:pressed {
                background-color: #D0D0D0;
            }
        """
        self.btn_new_folder.setStyleSheet(btn_style)
        self.btn_new_topic.setStyleSheet(btn_style)

        btn_row.addWidget(self.btn_new_folder)
        btn_row.addWidget(self.btn_new_topic)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # ========== Дерево тем ==========
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(20)  # ← отступ для вложенных элементов
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #DDD;
                border-radius: 6px;
                background-color: white;
                outline: none;
            }
            QTreeWidget::item {
                padding: 6px 4px;
                border-bottom: 1px solid #EEE;
            }
            QTreeWidget::item:hover {
                background-color: #F5F5F5;
            }
            QTreeWidget::item:selected {
                background-color: #E3F2FD;
                color: #000;
            }
        """)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._open_context_menu)
        self.tree.itemClicked.connect(self._on_item_clicked)

        layout.addWidget(self.tree)

        # Подключаем кнопки
        self.btn_new_folder.clicked.connect(self._create_folder)
        self.btn_new_topic.clicked.connect(self._create_topic)

        # Загружаем темы
        self.load_topics()

    # ---------------------------------------------------------
    # ЗАГРУЗКА И ПОИСК
    # ---------------------------------------------------------
    def load_topics(self):
        self.all_topics = self.topic_controller.get_all_topics()
        self._build_tree(self.all_topics)

    def _build_tree(self, topics):
        self.tree.clear()
        items_map = {}

        for topic in topics:
            item = QTreeWidgetItem()
            icon = "📁" if topic.type == "folder" else "📄"
            item.setText(0, f"{icon} {topic.name}")
            item.setData(0, Qt.UserRole, topic.id)
            items_map[topic.id] = item

        for topic in topics:
            item = items_map[topic.id]
            if topic.parent_id is None:
                self.tree.addTopLevelItem(item)
            else:
                parent_item = items_map.get(topic.parent_id)
                if parent_item:
                    parent_item.addChild(item)

        self.tree.expandAll()

    def _filter_topics(self, text: str):
        if not text.strip():
            self._build_tree(self.all_topics)
            return
        text_lower = text.lower()
        filtered = [t for t in self.all_topics if text_lower in t.name.lower()]
        self._build_tree(filtered)

    # ---------------------------------------------------------
    # ОПЕРАЦИИ С ТЕМАМИ
    # ---------------------------------------------------------
    def _get_selected_topic_id(self):
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
        topic_id = item.data(0, Qt.UserRole)
        if not topic_id:
            return

        all_topics = self.topic_controller.get_all_topics()
        folders = [t for t in all_topics if t.type == "folder" and t.id != topic_id]

        if not folders:
            QMessageBox.information(self, "Перемещение", "Нет доступных папок для перемещения.")
            return

        folder_names = [f"📁 {t.name}" for t in folders]
        folder_names.insert(0, "📁 Корень (без папки)")

        folder_name, ok = QInputDialog.getItem(
            self, "Переместить",
            "Выберите папку назначения:",
            folder_names, 0, False
        )
        if ok and folder_name:
            if folder_name == "📁 Корень (без папки)":
                new_parent_id = None
            else:
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
            topic = self.topic_controller.get_topic(topic_id)
            if topic and topic.type == "topic":
                self.topic_selected.emit(topic_id)