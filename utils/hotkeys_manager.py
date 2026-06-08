# managers/hotkeys_manager.py
"""
HotkeysManager — менеджер глобальных горячих клавиш.

Реализует:
- регистрацию хоткеев
- привязку действий к сочетаниям клавиш
- единый интерфейс для UI

Используется в главном окне приложения.
"""

from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QWidget


class HotkeysManager:
    """
    Менеджер горячих клавиш.
    Привязывается к главному окну или любому QWidget.
    """

    def __init__(self, parent: QWidget):
        self.parent = parent
        self.shortcuts = {}

    # ---------------------------------------------------------
    # РЕГИСТРАЦИЯ ХОТКЕЯ
    # ---------------------------------------------------------
    def register(self, key: str, callback):
        """
        Регистрирует горячую клавишу.
        key — строка формата "Ctrl+S", "Ctrl+Shift+N", "F5"
        callback — функция, вызываемая при нажатии
        """
        shortcut = QShortcut(QKeySequence(key), self.parent)
        shortcut.activated.connect(callback)
        self.shortcuts[key] = shortcut

    # ---------------------------------------------------------
    # УДАЛЕНИЕ ХОТКЕЯ
    # ---------------------------------------------------------
    def unregister(self, key: str):
        """
        Удаляет горячую клавишу.
        """
        if key in self.shortcuts:
            self.shortcuts[key].setParent(None)
            del self.shortcuts[key]

    # ---------------------------------------------------------
    # ОЧИСТКА ВСЕХ ХОТКЕЕВ
    # ---------------------------------------------------------
    def clear(self):
        """
        Удаляет все зарегистрированные хоткеи.
        """
        for sc in self.shortcuts.values():
            sc.setParent(None)
        self.shortcuts.clear()
