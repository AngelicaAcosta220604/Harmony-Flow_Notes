# Кастомное дерево тем
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QPushButton,
    QMenu
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QPoint


class TreeWidget(QWidget):
    """
    Прототип дерева тем.
    Поддерживает:
    - папки и темы
    - раскрытие/сворачивание
    - контекстное меню
    - кнопки создания папки/тем
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # ---------------------------------------------------------
        # Дерево
        # ---------------------------------------------------------
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._open_context_menu)

        self.layout.addWidget(self.tree)

        # ---------------------------------------------------------
        # Нижняя панель кнопок
        # ---------------------------------------------------------
        btn_row = QHBoxLayout()

        self.btn_new_folder = QPushButton("+ Новая папка")
        self.btn_new_topic = QPushButton("+ Новая тема")

        btn_row.addWidget(self.btn_new_folder)
        btn_row.addWidget(self.btn_new_topic)

        self.layout.addLayout(btn_row)

    # ---------------------------------------------------------
    # Методы работы с деревом
    # ---------------------------------------------------------

    def clear(self):
        self.tree.clear()

    def add_folder(self, name: str, parent_item=None):
        """Добавляет папку."""
        item = QTreeWidgetItem([name])
        item.setData(0, Qt.UserRole, "folder")
        item.setText(0, f"📁 {name}")

        if parent_item:
            parent_item.addChild(item)
        else:
            self.tree.addTopLevelItem(item)

        return item

    def add_topic(self, name: str, parent_item=None):
        """Добавляет тему."""
        item = QTreeWidgetItem([name])
        item.setData(0, Qt.UserRole, "topic")
        item.setText(0, f"📄 {name}")

        if parent_item:
            parent_item.addChild(item)
        else:
            self.tree.addTopLevelItem(item)

        return item

    def get_selected_item(self):
        items = self.tree.selectedItems()
        return items[0] if items else None

    # ---------------------------------------------------------
    # Контекстное меню
    # ---------------------------------------------------------

    def _open_context_menu(self, pos: QPoint):
        item = self.get_selected_item()
        if not item:
            return

        menu = QMenu(self)

        rename_action = QAction("Переименовать", self)
        delete_action = QAction("Удалить", self)
        move_action = QAction("Переместить", self)

        menu.addAction(rename_action)
        menu.addAction(delete_action)
        menu.addAction(move_action)

        rename_action.triggered.connect(lambda: self._emit_action("rename", item))
        delete_action.triggered.connect(lambda: self._emit_action("delete", item))
        move_action.triggered.connect(lambda: self._emit_action("move", item))

        menu.exec(self.tree.mapToGlobal(pos))

    # ---------------------------------------------------------
    # Сигналы-заглушки
    # ---------------------------------------------------------

    def _emit_action(self, action: str, item: QTreeWidgetItem):
        print(f"[TreeWidget] Action: {action} → {item.text(0)}")
