# widgets/rich_text_editor.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QComboBox, QColorDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QTextCharFormat, QTextCursor, QFont, QColor,
    QTextListFormat, QTextBlockFormat, QAction  # QAction здесь!
)


class RichTextEditor(QWidget):
    """Полноценный WYSIWYG редактор с форматированием"""

    text_changed = Signal()  # сигнал при изменении текста

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
        self._update_format_buttons()

    def setup_ui(self):
        """Создаёт интерфейс редактора"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # ========== Панель инструментов ==========
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # ========== Редактор ==========
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(True)
        self.editor.setStyleSheet("""
            QTextEdit {
                border: 1px solid #DDD;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self.editor)

    def _create_toolbar(self):
        """Создаёт панель инструментов"""
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: #F5F5F5; border-radius: 4px; padding: 5px;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setSpacing(4)

        # ---------------------------------------------------------
        # B, I, U
        # ---------------------------------------------------------
        self.btn_bold = QPushButton("B")
        self.btn_bold.setToolTip("Жирный (Ctrl+B)")
        self.btn_bold.setFixedSize(32, 28)
        self.btn_bold.setCheckable(True)

        self.btn_italic = QPushButton("I")
        self.btn_italic.setToolTip("Курсив (Ctrl+I)")
        self.btn_italic.setFixedSize(32, 28)
        self.btn_italic.setCheckable(True)

        self.btn_underline = QPushButton("U")
        self.btn_underline.setToolTip("Подчёркнутый (Ctrl+U)")
        self.btn_underline.setFixedSize(32, 28)
        self.btn_underline.setCheckable(True)

        toolbar_layout.addWidget(self.btn_bold)
        toolbar_layout.addWidget(self.btn_italic)
        toolbar_layout.addWidget(self.btn_underline)

        toolbar_layout.addSpacing(15)

        # ---------------------------------------------------------
        # H1, H2, H3 + размер шрифта
        # ---------------------------------------------------------
        self.btn_h1 = QPushButton("H1")
        self.btn_h1.setToolTip("Заголовок 1")
        self.btn_h1.setFixedSize(40, 28)

        self.btn_h2 = QPushButton("H2")
        self.btn_h2.setToolTip("Заголовок 2")
        self.btn_h2.setFixedSize(40, 28)

        self.btn_h3 = QPushButton("H3")
        self.btn_h3.setToolTip("Заголовок 3")
        self.btn_h3.setFixedSize(40, 28)

        toolbar_layout.addWidget(self.btn_h1)
        toolbar_layout.addWidget(self.btn_h2)
        toolbar_layout.addWidget(self.btn_h3)

        toolbar_layout.addSpacing(10)

        # Размер шрифта
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(
            ['8', '9', '10', '11', '12', '14', '16', '18', '20', '24', '28', '32', '36', '48']
        )
        self.font_size_combo.setCurrentText('12')
        self.font_size_combo.setFixedWidth(60)
        self.font_size_combo.setEditable(True)
        toolbar_layout.addWidget(self.font_size_combo)

        toolbar_layout.addSpacing(15)

        # ---------------------------------------------------------
        # Списки
        # ---------------------------------------------------------
        self.btn_list = QPushButton("• Список")
        self.btn_list.setToolTip("Маркированный список")
        self.btn_list.setFixedSize(80, 28)
        self.btn_list.setCheckable(False)

        toolbar_layout.addWidget(self.btn_list)

        toolbar_layout.addSpacing(15)

        # ---------------------------------------------------------
        # Цвета
        # ---------------------------------------------------------
        self.btn_text_color = QPushButton("🎨 Цвет")
        self.btn_text_color.setToolTip("Цвет текста")
        self.btn_text_color.setFixedSize(70, 28)

        self.btn_bg_color = QPushButton("М")
        self.btn_bg_color.setToolTip("Выделение цветом фона (маркер)")
        self.btn_bg_color.setFixedSize(32, 28)

        toolbar_layout.addWidget(self.btn_text_color)
        toolbar_layout.addWidget(self.btn_bg_color)

        toolbar_layout.addStretch()

        return toolbar

    def connect_signals(self):
        """Подключает сигналы"""
        # Форматирование
        self.btn_bold.clicked.connect(self.toggle_bold)
        self.btn_italic.clicked.connect(self.toggle_italic)
        self.btn_underline.clicked.connect(self.toggle_underline)

        # Заголовки
        self.btn_h1.clicked.connect(lambda: self.apply_heading(1))
        self.btn_h2.clicked.connect(lambda: self.apply_heading(2))
        self.btn_h3.clicked.connect(lambda: self.apply_heading(3))

        # Размер шрифта
        self.font_size_combo.currentTextChanged.connect(self.apply_font_size)

        # Списки
        self.btn_list.clicked.connect(self.toggle_list)

        # Цвета
        self.btn_text_color.clicked.connect(self.set_text_color)
        self.btn_bg_color.clicked.connect(self.set_background_color)

        # Отслеживание позиции курсора
        self.editor.cursorPositionChanged.connect(self._update_format_buttons)

    # ==================== ФОРМАТИРОВАНИЕ ТЕКСТА ====================

    def toggle_bold(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Bold if self.btn_bold.isChecked() else QFont.Normal)
            cursor.mergeCharFormat(fmt)
        else:
            self.editor.setFontWeight(QFont.Bold if self.btn_bold.isChecked() else QFont.Normal)

    def toggle_italic(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFontItalic(self.btn_italic.isChecked())
            cursor.mergeCharFormat(fmt)
        else:
            self.editor.setFontItalic(self.btn_italic.isChecked())

    def toggle_underline(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFontUnderline(self.btn_underline.isChecked())
            cursor.mergeCharFormat(fmt)
        else:
            self.editor.setFontUnderline(self.btn_underline.isChecked())

    def apply_heading(self, level: int):
        """Применяет заголовок к текущему блоку"""
        cursor = self.editor.textCursor()
        sizes = {1: 24, 2: 18, 3: 14}
        weights = {1: QFont.Bold, 2: QFont.Bold, 3: QFont.Normal}

        fmt = QTextCharFormat()
        fmt.setFontPointSize(sizes.get(level, 12))
        fmt.setFontWeight(weights.get(level, QFont.Normal))

        cursor.select(QTextCursor.BlockUnderCursor)
        cursor.mergeCharFormat(fmt)

    def apply_font_size(self, size_text: str):
        """Применяет размер шрифта"""
        try:
            size = float(size_text)
            cursor = self.editor.textCursor()
            fmt = QTextCharFormat()
            fmt.setFontPointSize(size)

            if cursor.hasSelection():
                cursor.mergeCharFormat(fmt)
            else:
                self.editor.setFontPointSize(size)
        except ValueError:
            pass

    # ==================== СПИСКИ ====================

    def toggle_list(self):
        """Переключает тип списка: маркированный -> нумерованный -> обычный текст"""
        cursor = self.editor.textCursor()
        current_list = cursor.currentList()

        if current_list is None:
            self._create_list(QTextListFormat.ListDisc)
            self.btn_list.setText("1. Список")
            self.btn_list.setToolTip("Нумерованный список")
        else:
            current_format = current_list.format()
            if current_format.style() == QTextListFormat.ListDisc:
                self._create_list(QTextListFormat.ListDecimal)
                self.btn_list.setText("✓ Список")
                self.btn_list.setToolTip("Обычный текст")
            elif current_format.style() == QTextListFormat.ListDecimal:
                self._remove_list()
                self.btn_list.setText("• Список")
                self.btn_list.setToolTip("Маркированный список")

    def _create_list(self, style):
        """Создаёт список указанного стиля"""
        cursor = self.editor.textCursor()
        list_format = QTextListFormat()
        list_format.setStyle(style)
        cursor.createList(list_format)

    def _remove_list(self):
        """Убирает форматирование списка"""
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.BlockUnderCursor)
        block_format = QTextBlockFormat()
        cursor.mergeBlockFormat(block_format)

    # ==================== ЦВЕТА ====================

    def set_text_color(self):
        """Выбор цвета текста"""
        color = QColorDialog.getColor()
        if color.isValid():
            cursor = self.editor.textCursor()
            fmt = QTextCharFormat()
            fmt.setForeground(color)

            if cursor.hasSelection():
                cursor.mergeCharFormat(fmt)
            else:
                self.editor.setTextColor(color)

    def set_background_color(self):
        """Выбор цвета фона (маркер)"""
        color = QColorDialog.getColor()
        if color.isValid():
            cursor = self.editor.textCursor()
            fmt = QTextCharFormat()
            fmt.setBackground(color)

            if cursor.hasSelection():
                cursor.mergeCharFormat(fmt)
            else:
                self.editor.setTextBackgroundColor(color)

    # ==================== ОБНОВЛЕНИЕ СОСТОЯНИЯ КНОПОК ====================

    def _update_format_buttons(self):
        """Обновляет состояние кнопок в зависимости от позиции курсора"""
        cursor = self.editor.textCursor()
        char_format = cursor.charFormat()

        # B, I, U
        self.btn_bold.setChecked(char_format.fontWeight() == QFont.Bold)
        self.btn_italic.setChecked(char_format.fontItalic())
        self.btn_underline.setChecked(char_format.fontUnderline())

        # Размер шрифта
        current_size = char_format.fontPointSize()
        if current_size > 0:
            self.font_size_combo.setCurrentText(str(int(current_size)))

        # Статус списка
        current_list = cursor.currentList()
        if current_list is None:
            self.btn_list.setText("• Список")
            self.btn_list.setToolTip("Маркированный список")
        else:
            list_format = current_list.format()
            if list_format.style() == QTextListFormat.ListDisc:
                self.btn_list.setText("1. Список")
                self.btn_list.setToolTip("Нумерованный список")
            else:
                self.btn_list.setText("✓ Список")
                self.btn_list.setToolTip("Обычный текст")

    # ==================== РАБОТА С ТЕКСТОМ ====================

    def to_html(self) -> str:
        return self.editor.toHtml()

    def to_plain_text(self) -> str:
        return self.editor.toPlainText()

    def set_html(self, html: str):
        if html:
            self.editor.setHtml(html)
        else:
            self.editor.clear()

    def set_plain_text(self, text: str):
        self.editor.setPlainText(text)

    def clear(self):
        self.editor.clear()

    def undo(self):
        self.editor.undo()

    def redo(self):
        self.editor.redo()

    def keyPressEvent(self, event):
        """Обработка горячих клавиш"""
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_B:
                self.btn_bold.click()
                event.accept()
                return
            elif event.key() == Qt.Key_I:
                self.btn_italic.click()
                event.accept()
                return
            elif event.key() == Qt.Key_U:
                self.btn_underline.click()
                event.accept()
                return
            elif event.key() == Qt.Key_Z:
                self.undo()
                event.accept()
                return
            elif event.key() == Qt.Key_Y:
                self.redo()
                event.accept()
                return
            elif event.key() == Qt.Key_S:
                # Сигнал для сохранения (будет обработан в NoteEditorView)
                self.text_changed.emit()
                event.accept()
                return

        # Enter в списке
        if event.key() == Qt.Key_Return:
            cursor = self.editor.textCursor()
            if cursor.currentList():
                if cursor.block().text().strip() == "":
                    self._remove_list()
                    event.accept()
                    return

        super().keyPressEvent(event)