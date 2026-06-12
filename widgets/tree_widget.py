# widgets/tree_widget.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QPushButton,
    QInputDialog, QLineEdit,
    QLabel, QMenu, QComboBox, QMessageBox,
)
from widgets.silent_dialog import SilentMessageBox, SilentInputDialog
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, Signal, QPoint
from controllers.topic_controller import TopicController


class TreeWidget(QWidget):
    topic_selected = Signal(int)
    topics_changed = Signal()

    def __init__(self, topic_controller: TopicController, parent=None):
        super().__init__(parent)
        self.topic_controller = topic_controller
        self.all_topics = []
        self.current_parent_id = None  # Для отслеживания выбранной папки

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

        # Дерево
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

        self.tree.setDragEnabled(False)
        self.tree.setAcceptDrops(False)
        self.tree.setDropIndicatorShown(False)

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._open_context_menu)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)

        layout.addWidget(self.tree)

        # Подключаем кнопки
        self.btn_new_folder.clicked.connect(self._create_folder_in_selected)
        self.btn_new_topic.clicked.connect(self._create_topic_in_selected)

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
        from services.time_service import TimeService

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
            item.setData(0, Qt.UserRole + 1, topic.type)  # Сохраняем тип
            items_map[topic.id] = item

            icon = "📁" if topic.type == "folder" else "📄"
            date_str = TimeService.format_display(topic.updated_at or topic.created_at)

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

        self.tree.collapseAll()

    # ==================== КОНТЕКСТНОЕ МЕНЮ ====================

    def _open_context_menu(self, pos: QPoint):
        item = self.tree.itemAt(pos)
        if not item:
            # Если клик на пустом месте — показываем меню создания в корне
            menu = QMenu(self)
            create_folder_action = QAction("📁 Создать папку", self)
            create_topic_action = QAction("📄 Создать тему", self)
            create_folder_action.triggered.connect(self._create_folder_in_root)
            create_topic_action.triggered.connect(self._create_topic_in_root)
            menu.addAction(create_folder_action)
            menu.addAction(create_topic_action)
            menu.exec(self.tree.mapToGlobal(pos))
            return

        topic_id = item.data(0, Qt.UserRole)
        if not topic_id:
            return

        topic = self.topic_controller.get_topic(topic_id)
        if not topic:
            return

        menu = QMenu(self)

        # Создание внутри папки
        if topic.type == "folder":
            create_folder_action = QAction("📁 Создать папку внутри", self)
            create_topic_action = QAction("📄 Создать тему внутри", self)
            create_folder_action.triggered.connect(lambda: self._create_folder_in_parent(topic_id))
            create_topic_action.triggered.connect(lambda: self._create_topic_in_parent(topic_id))
            menu.addAction(create_folder_action)
            menu.addAction(create_topic_action)
            menu.addSeparator()

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

    # ==================== СОЗДАНИЕ ЭЛЕМЕНТОВ ====================

    def _get_selected_folder_id(self):
        """Возвращает ID выбранной папки или None, если выбрана тема или ничего."""
        current_item = self.tree.currentItem()
        if not current_item:
            return None

        topic_id = current_item.data(0, Qt.UserRole)
        if not topic_id:
            return None

        topic = self.topic_controller.get_topic(topic_id)
        if topic and topic.type == "folder":
            return topic_id
        return None

    def _create_folder_in_root(self):
        """Создаёт папку в корне."""
        self._create_folder_in_parent(None)

    def _create_topic_in_root(self):
        """Создаёт тему в корне."""
        self._create_topic_in_parent(None)

    def _create_folder_in_parent(self, parent_id):
        """Создаёт папку внутри указанной родительской папки."""
        name, ok = SilentInputDialog.getText(self, "Новая папка", "Введите название папки:")
        if ok and name.strip():
            try:
                self.topic_controller.add_topic(name.strip(), parent_id=parent_id, type="folder")
                self.load_topics()
                self.topics_changed.emit()
            except ValueError as e:
                SilentMessageBox.warning(self, "Ошибка", str(e))

    def _create_topic_in_parent(self, parent_id):
        """Создаёт тему внутри указанной родительской папки."""
        name, ok = SilentInputDialog.getText(self, "Новая тема", "Введите название темы:")
        if ok and name.strip():
            try:
                self.topic_controller.add_topic(name.strip(), parent_id=parent_id, type="topic")
                self.load_topics()
                self.topics_changed.emit()
            except ValueError as e:
                SilentMessageBox.warning(self, "Ошибка", str(e))

    def _create_folder_in_selected(self):
        """Создаёт папку внутри выбранной папки (или в корне)."""
        parent_id = self._get_selected_folder_id()
        self._create_folder_in_parent(parent_id)

    def _create_topic_in_selected(self):
        """Создаёт тему внутри выбранной папки (или в корне)."""
        parent_id = self._get_selected_folder_id()
        self._create_topic_in_parent(parent_id)

    # ==================== ПЕРЕМЕЩЕНИЕ ====================

    def _move_topic(self, topic_id: int, name: str):
        current = self.topic_controller.get_topic(topic_id)
        if not current:
            return

        # Собираем список папок для перемещения (исключая себя)
        folders = [t for t in self.all_topics if t.type == "folder" and t.id != topic_id]

        # Добавляем опцию корня
        folder_names = ["📁 Корень (без папки)"]

        # Также нельзя перемещать в самого себя и в свои дочерние элементы
        for f in folders:
            # Проверяем, не является ли папка потомком перемещаемой папки
            is_child = self._is_child_of(f.id, topic_id) if current.type == "folder" else False
            if not is_child:
                folder_names.append(f"📁 {f.name}")
            else:
                folder_names.append(f"📁 {f.name} (нельзя - вложенная папка)")

        from PySide6.QtWidgets import QInputDialog
        folder_name, ok = QInputDialog.getItem(
            self, "Переместить",
            f"Куда переместить «{name}»?",
            folder_names, 0, False
        )

        if ok and folder_name:
            if folder_name == "📁 Корень (без папки)":
                new_parent_id = None
            elif " (нельзя" in folder_name:
                SilentMessageBox.warning(self, "Ошибка", "Нельзя переместить папку в её собственную вложенную папку")
                return
            else:
                # Находим ID папки по имени
                clean_name = folder_name.replace("📁 ", "")
                for f in folders:
                    if f.name == clean_name:
                        new_parent_id = f.id
                        break
                else:
                    return

            try:
                self.topic_controller.move_topic(topic_id, new_parent_id)
                self.load_topics()
                self.topics_changed.emit()
                SilentMessageBox.information(self, "Готово", f"«{name}» перемещена")
            except ValueError as e:
                SilentMessageBox.warning(self, "Ошибка", str(e))

    def _is_child_of(self, child_id: int, parent_id: int) -> bool:
        """Проверяет, является ли child_id потомком parent_id."""
        if child_id == parent_id:
            return True

        child = self.topic_controller.get_topic(child_id)
        if not child or child.parent_id is None:
            return False

        return self._is_child_of(child.parent_id, parent_id)

    # ==================== ОПЕРАЦИИ ====================

    def _rename_topic(self, topic_id: int, old_name: str):
        new_name, ok = SilentInputDialog.getText(self, "Переименовать", "Новое название:", text=old_name)
        if ok and new_name.strip():
            try:
                self.topic_controller.rename_topic(topic_id, new_name.strip())
                self.load_topics()
                self.topics_changed.emit()
            except ValueError as e:
                SilentMessageBox.warning(self, "Ошибка", str(e))

    def _delete_topic(self, topic_id: int, name: str):
        reply = SilentMessageBox.question(
            self, "Удаление",
            f"Удалить «{name}» и всё содержимое?"
        )
        if reply == QMessageBox.Yes:
            self.topic_controller.delete_topic(topic_id)
            self.load_topics()
            self.topics_changed.emit()

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Одиночный клик — запоминаем выбранный элемент."""
        topic_id = item.data(0, Qt.UserRole)
        if topic_id:
            topic = self.topic_controller.get_topic(topic_id)
            if topic and topic.type == "folder":
                # Запоминаем выбранную папку
                self.current_parent_id = topic_id
            elif topic and topic.type == "topic":
                # Для темы тоже запоминаем её родителя
                self.current_parent_id = topic.parent_id

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Двойной клик — открываем тему или раскрываем/схлопываем папку."""
        topic_id = item.data(0, Qt.UserRole)
        if not topic_id:
            return

        topic = self.topic_controller.get_topic(topic_id)
        if not topic:
            return

        if topic.type == "topic":
            # Открываем тему
            self.topic_selected.emit(topic_id)
        else:
            # Для папки — раскрываем/схлопываем
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)