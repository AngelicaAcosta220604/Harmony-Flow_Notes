# widgets/tree_widget.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QPushButton,
    QInputDialog, QLineEdit,
    QLabel, QMenu, QComboBox, QMessageBox
)

from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, Signal, QPoint
from controllers.topic_controller import TopicController


class TreeWidget(QWidget):
    topic_selected = Signal(int)

    def __init__(self, topic_controller: TopicController, parent=None):
        super().__init__(parent)
        self.topic_controller = topic_controller
        self.all_topics = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Поиск
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск по темам...")
        self.search_input.setMinimumHeight(32)
        self.search_input.textChanged.connect(self._filter_topics)
        layout.addWidget(self.search_input)

        # Сортировка
        sort_row = QHBoxLayout()
        sort_label = QLabel("Сортировать:")
        sort_label.setStyleSheet("font-size: 12px;")
        sort_row.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.addItem("📅 Новые → Старые")
        self.sort_combo.addItem("📅 Старые → Новые")
        self.sort_combo.addItem("🔤 А → Я")
        self.sort_combo.addItem("🔤 Я → А")
        self.sort_combo.setCurrentIndex(0)
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        sort_row.addWidget(self.sort_combo)
        sort_row.addStretch()
        layout.addLayout(sort_row)

        # Кнопки
        btn_row = QHBoxLayout()
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
            QPushButton:hover { background-color: #E0E0E0; }
        """
        self.btn_new_folder.setStyleSheet(btn_style)
        self.btn_new_topic.setStyleSheet(btn_style)
        btn_row.addWidget(self.btn_new_folder)
        btn_row.addWidget(self.btn_new_topic)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Дерево (drag & drop ОТКЛЮЧЁН)
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(20)
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #DDD;
                border-radius: 6px;
                background-color: white;
                outline: none;
            }
            QTreeWidget::item {
                padding: 8px 4px;
                border-bottom: 1px solid #EEE;
            }
            QTreeWidget::item:hover {
                background-color: #F5F5F5;
            }
            QTreeWidget::item:selected {
                background-color: #51b2c1;
            }
        """)

        # Drag & drop ОТКЛЮЧЁН
        self.tree.setDragEnabled(False)
        self.tree.setAcceptDrops(False)
        self.tree.setDropIndicatorShown(False)

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._open_context_menu)
        self.tree.itemClicked.connect(self._on_item_clicked)

        layout.addWidget(self.tree)

        # Подключаем кнопки
        self.btn_new_folder.clicked.connect(self._create_folder)
        self.btn_new_topic.clicked.connect(self._create_topic)

        self.load_topics()

    # ==================== ЗАГРУЗКА И СОРТИРОВКА ====================

    def load_topics(self):
        self.all_topics = self.topic_controller.get_all_topics()
        self._apply_filter_and_sort()

    def _on_sort_changed(self):
        self._apply_filter_and_sort()

    def _filter_topics(self, text: str):
        self._apply_filter_and_sort()

    def _apply_filter_and_sort(self):
        filter_text = self.search_input.text()

        if filter_text:
            text_lower = filter_text.lower()
            filtered = [t for t in self.all_topics if text_lower in t.name.lower()]
        else:
            filtered = self.all_topics.copy()

        sort_index = self.sort_combo.currentIndex()

        folders = [t for t in filtered if t.type == "folder"]
        topics = [t for t in filtered if t.type == "topic"]

        if sort_index == 0:  # Новые → Старые
            folders.sort(key=lambda x: x.created_at or "", reverse=True)
            topics.sort(key=lambda x: x.created_at or "", reverse=True)
        elif sort_index == 1:  # Старые → Новые
            folders.sort(key=lambda x: x.created_at or "", reverse=False)
            topics.sort(key=lambda x: x.created_at or "", reverse=False)
        elif sort_index == 2:  # А → Я
            folders.sort(key=lambda x: x.name.lower())
            topics.sort(key=lambda x: x.name.lower())
        elif sort_index == 3:  # Я → А
            folders.sort(key=lambda x: x.name.lower(), reverse=True)
            topics.sort(key=lambda x: x.name.lower(), reverse=True)

        sorted_topics = folders + topics
        self._build_tree(sorted_topics)

    def _build_tree(self, topics):
        self.tree.clear()

        if not topics:
            empty_item = QTreeWidgetItem()
            empty_item.setText(0, "📭 Нет тем. Создайте первую тему!")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsSelectable)
            self.tree.addTopLevelItem(empty_item)
            return

        items_map = {}

        for topic in topics:
            item = QTreeWidgetItem()
            item.setData(0, Qt.UserRole, topic.id)
            items_map[topic.id] = item

            icon = "📁" if topic.type == "folder" else "📄"
            date_str = ""
            if topic.updated_at:
                date_str = topic.updated_at[:16]
            elif topic.created_at:
                date_str = topic.created_at[:16]

            if date_str:
                display_text = f"{icon} {topic.name}   {date_str}"
            else:
                display_text = f"{icon} {topic.name}"
            item.setText(0, display_text)

        for topic in topics:
            item = items_map[topic.id]
            if topic.parent_id is None:
                self.tree.addTopLevelItem(item)
            else:
                parent_item = items_map.get(topic.parent_id)
                if parent_item:
                    parent_item.addChild(item)
                else:
                    self.tree.addTopLevelItem(item)

        # Папки СВЁРНУТЫ по умолчанию
        self.tree.collapseAll()

    # ==================== КОНТЕКСТНОЕ МЕНЮ ====================

    def _open_context_menu(self, pos: QPoint):
        item = self.tree.itemAt(pos)
        if not item:
            return

        topic_id = item.data(0, Qt.UserRole)
        if not topic_id:
            return

        topic = self.topic_controller.get_topic(topic_id)
        if not topic:
            return

        menu = QMenu(self)

        rename_action = QAction("✏️ Переименовать", self)
        delete_action = QAction("🗑️ Удалить", self)
        move_action = QAction("📁 Переместить в папку", self)

        menu.addAction(rename_action)
        menu.addAction(delete_action)
        menu.addSeparator()
        menu.addAction(move_action)

        rename_action.triggered.connect(lambda: self._rename_topic(topic_id, topic.name))
        delete_action.triggered.connect(lambda: self._delete_topic(topic_id, topic.name))
        move_action.triggered.connect(lambda: self._move_topic(topic_id, topic.name))

        menu.exec(self.tree.mapToGlobal(pos))

    def _move_topic(self, topic_id: int, name: str):
        folders = [t for t in self.all_topics if t.type == "folder" and t.id != topic_id]

        if not folders:
            QMessageBox.information(self, "Перемещение", "Нет доступных папок для перемещения.")
            return

        folder_names = ["📁 Корень (без папки)"] + [f"📁 {f.name}" for f in folders]

        folder_name, ok = QInputDialog.getItem(
            self, "Переместить",
            f"Куда переместить «{name}»?",
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
            QMessageBox.information(self, "Готово", f"«{name}» перемещена")

    # ==================== ОПЕРАЦИИ ====================

    def _create_folder(self):
        name, ok = QInputDialog.getText(self, "Новая папка", "Введите название папки:")
        if ok and name.strip():
            self.topic_controller.add_topic(name.strip(), parent_id=None, type="folder")
            self.load_topics()

    def _create_topic(self):
        name, ok = QInputDialog.getText(self, "Новая тема", "Введите название темы:")
        if ok and name.strip():
            self.topic_controller.add_topic(name.strip(), parent_id=None, type="topic")
            self.load_topics()

    def _rename_topic(self, topic_id: int, old_name: str):
        new_name, ok = QInputDialog.getText(self, "Переименовать", "Новое название:", text=old_name)
        if ok and new_name.strip():
            self.topic_controller.rename_topic(topic_id, new_name.strip())
            self.load_topics()

    def _delete_topic(self, topic_id: int, name: str):
        reply = QMessageBox.question(
            self, "Удаление",
            f"Удалить «{name}» и всё содержимое?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.topic_controller.delete_topic(topic_id)
            self.load_topics()

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        topic_id = item.data(0, Qt.UserRole)
        if topic_id:
            topic = self.topic_controller.get_topic(topic_id)
            if topic and topic.type == "topic":
                self.topic_selected.emit(topic_id)