# widgets/topic_tree_selector.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QCheckBox, QLineEdit, QComboBox, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt


class TopicTreeSelector(QWidget):
    """Дерево тем с чекбоксами для выбора и отображением карточек внутри тем"""

    def __init__(self, topic_controller, flashcard_controller, parent=None):
        super().__init__(parent)
        self.topic_controller = topic_controller
        self.flashcard_controller = flashcard_controller
        self.all_topics = []
        self.filtered_topics = []
        self.all_cards = {}
        self.current_sort = "alpha"
        self.current_filter = ""
        self.card_filter = "all"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Панель управления
        control_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск по темам...")
        self.search_input.textChanged.connect(self._on_search_changed)
        control_layout.addWidget(self.search_input, 2)

        self.sort_combo = QComboBox()
        self.sort_combo.addItem("🔤 А → Я", "alpha")
        self.sort_combo.addItem("🔤 Я → А", "alpha_reverse")
        self.sort_combo.addItem("📅 Новые → Старые", "date_new")
        self.sort_combo.addItem("📅 Старые → Новые", "date_old")
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        control_layout.addWidget(self.sort_combo)

        self.card_filter_combo = QComboBox()
        self.card_filter_combo.addItem("📋 Все карточки", "all")
        self.card_filter_combo.addItem("📝 Свободные", "free")
        self.card_filter_combo.addItem("❓ Вопрос-Ответ", "qa")
        self.card_filter_combo.currentIndexChanged.connect(self._on_card_filter_changed)
        control_layout.addWidget(self.card_filter_combo)

        layout.addLayout(control_layout)

        # Дерево
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(20)
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #DDD;
                border-radius: 6px;
                background-color: white;
                min-height: 300px;
            }
            QTreeWidget::item {
                padding: 6px 4px;
            }
            QTreeWidget::item:hover {
                background-color: #57c5a4;
            }
        """)
        self.tree.setColumnCount(1)
        self.tree.header().setStretchLastSection(True)

        layout.addWidget(self.tree)

        self.load_data()

    def _on_search_changed(self, text: str):
        self.current_filter = text.strip().lower()
        self._apply_filter_and_sort()

    def _on_sort_changed(self):
        self.current_sort = self.sort_combo.currentData()
        self._apply_filter_and_sort()

    def _on_card_filter_changed(self):
        self.card_filter = self.card_filter_combo.currentData()
        self.load_data()

    def _apply_filter_and_sort(self):
        if not self.all_topics:
            return
        if self.current_filter:
            self.filtered_topics = [t for t in self.all_topics if self.current_filter in t.name.lower()]
        else:
            self.filtered_topics = self.all_topics.copy()
        self._build_tree()

    def load_data(self):
        self.all_topics = self.topic_controller.get_all_topics()
        self.all_cards = {}
        for topic in self.all_topics:
            if topic.type == "topic":
                cards = self.flashcard_controller.get_cards_by_topic(topic.id)
                if self.card_filter == "free":
                    cards = [c for c in cards if c.type == "free"]
                elif self.card_filter == "qa":
                    cards = [c for c in cards if c.type == "qa"]
                self.all_cards[topic.id] = cards
            else:
                self.all_cards[topic.id] = []
        self.filtered_topics = self.all_topics.copy()
        self._build_tree()

    def _build_tree(self):
        self.tree.clear()

        if not self.filtered_topics:
            empty_item = QTreeWidgetItem()
            empty_item.setText(0, "📭 Нет тем")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsSelectable)
            self.tree.addTopLevelItem(empty_item)
            return

        self._sort_topics_list()
        items_map = {}

        # Создаём элементы для папок и тем
        for topic in self.filtered_topics:
            item = QTreeWidgetItem()
            item.setData(0, Qt.UserRole, topic.id)
            item.setData(0, Qt.UserRole + 1, "topic")
            items_map[topic.id] = item

            icon = "📁" if topic.type == "folder" else "📄"
            item.setText(0, f"{icon} {topic.name}")

            # Включаем чекбокс у элемента
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked)

            items_map[topic.id] = item

        # Выстраиваем иерархию
        for topic in self.filtered_topics:
            item = items_map[topic.id]
            if topic.parent_id is None or topic.parent_id not in items_map:
                self.tree.addTopLevelItem(item)
            else:
                parent_item = items_map.get(topic.parent_id)
                if parent_item:
                    parent_item.addChild(item)
                else:
                    self.tree.addTopLevelItem(item)

        # Добавляем карточки как дочерние элементы тем
        for topic in self.filtered_topics:
            if topic.type == "topic":
                topic_item = items_map[topic.id]
                cards = self.all_cards.get(topic.id, [])

                for card in cards:
                    card_item = QTreeWidgetItem()
                    card_item.setData(0, Qt.UserRole, card.id)
                    card_item.setData(0, Qt.UserRole + 1, "card")

                    status_icon = ""
                    if card.review_status == "new":
                        status_icon = "🆕"
                    elif card.review_status == "learning":
                        status_icon = "📖"
                    elif card.review_status == "review":
                        status_icon = "✅"

                    if card.type == "free":
                        content = card.content[:50] + "..." if len(card.content or "") > 50 else (card.content or "")
                        card_item.setText(0, f"     📝 {status_icon} {content}")
                    else:
                        question = card.question[:50] + "..." if len(card.question or "") > 50 else (
                                    card.question or "")
                        card_item.setText(0, f"     ❓ {status_icon} {question}")

                    # Включаем чекбокс для карточки
                    card_item.setFlags(card_item.flags() | Qt.ItemIsUserCheckable)
                    card_item.setCheckState(0, Qt.Unchecked)

                    topic_item.addChild(card_item)

        self.tree.collapseAll()

    def _sort_topics_list(self):
        if self.current_sort == "alpha":
            self.filtered_topics.sort(key=lambda x: x.name.lower())
        elif self.current_sort == "alpha_reverse":
            self.filtered_topics.sort(key=lambda x: x.name.lower(), reverse=True)
        elif self.current_sort == "date_new":
            self.filtered_topics.sort(key=lambda x: x.created_at or "", reverse=True)
        elif self.current_sort == "date_old":
            self.filtered_topics.sort(key=lambda x: x.created_at or "", reverse=False)

    def get_selected_topic_ids(self) -> list:
        """Возвращает список ID выбранных тем (где чекбокс включён)"""
        selected_ids = []

        def walk_items(item):
            item_type = item.data(0, Qt.UserRole + 1)
            if item_type == "topic":
                topic_id = item.data(0, Qt.UserRole)
                if topic_id and item.checkState(0) == Qt.Checked:
                    selected_ids.append(topic_id)
            for i in range(item.childCount()):
                walk_items(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            walk_items(self.tree.topLevelItem(i))

        return selected_ids

    def get_selected_card_ids(self) -> list:
        """Возвращает список ID выбранных карточек"""
        selected_ids = []

        def walk_items(item):
            item_type = item.data(0, Qt.UserRole + 1)
            if item_type == "card":
                card_id = item.data(0, Qt.UserRole)
                if card_id and item.checkState(0) == Qt.Checked:
                    selected_ids.append(card_id)
            for i in range(item.childCount()):
                walk_items(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            walk_items(self.tree.topLevelItem(i))

        return selected_ids

    def select_all(self):
        """Выбирает всё"""

        def check_all(item):
            item.setCheckState(0, Qt.Checked)
            for i in range(item.childCount()):
                check_all(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            check_all(self.tree.topLevelItem(i))

    def clear_all(self):
        """Снимает всё выделение"""

        def uncheck_all(item):
            item.setCheckState(0, Qt.Unchecked)
            for i in range(item.childCount()):
                uncheck_all(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            uncheck_all(self.tree.topLevelItem(i))

    def refresh(self):
        old_selected_topics = self.get_selected_topic_ids()
        old_selected_cards = self.get_selected_card_ids()
        self.load_data()
        self._restore_selection(old_selected_topics, old_selected_cards)

    def _restore_selection(self, topic_ids, card_ids):
        """Восстанавливает выделение после обновления"""

        def restore(item):
            item_type = item.data(0, Qt.UserRole + 1)
            item_id = item.data(0, Qt.UserRole)
            if item_type == "topic" and item_id in topic_ids:
                item.setCheckState(0, Qt.Checked)
            elif item_type == "card" and item_id in card_ids:
                item.setCheckState(0, Qt.Checked)
            for i in range(item.childCount()):
                restore(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            restore(self.tree.topLevelItem(i))