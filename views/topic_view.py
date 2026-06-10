# views/topic_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QListWidget, QPushButton, QListWidgetItem,
    QMessageBox, QInputDialog, QFrame, QStackedWidget, QMenu, QLineEdit
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QComboBox, QGridLayout, QScrollArea


class TopicView(QWidget):
    back_requested = Signal()  # возврат к списку тем

    def __init__(self, topic_id: int, topic_controller, note_controller,
                 flashcard_controller, task_controller, session_controller,
                 parent=None):
        super().__init__(parent)
        self.topic_id = topic_id
        self.topic_controller = topic_controller
        self.note_controller = note_controller
        self.flashcard_controller = flashcard_controller
        self.task_controller = task_controller
        self.session_controller = session_controller

        # Загружаем тему
        self.topic = self.topic_controller.get_topic(topic_id)

        self.current_view_mode = "list"  # "list" или "grid"
        self.current_sort_by = "date"  # "date" или "alpha"
        # Основной лэйаут
        main_layout = QVBoxLayout(self)

        # ========== Верхняя панель с кнопкой "Назад" ==========
        top_bar = QHBoxLayout()
        self.back_button = QPushButton("← Назад к темам")
        self.back_button.clicked.connect(self.back_requested.emit)
        top_bar.addWidget(self.back_button)
        top_bar.addStretch()

        title_label = QLabel(self.topic.name)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        top_bar.addWidget(title_label)
        top_bar.addStretch()

        if hasattr(self.topic, 'updated_at') and self.topic.updated_at:
            date_label = QLabel(f"Изменено: {self.topic.updated_at[:16]}")
            date_label.setStyleSheet("color: gray; font-size: 12px;")
            top_bar.addWidget(date_label)

        main_layout.addLayout(top_bar)

        # ========== Основное содержимое: левое меню + правая область ==========
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # ---------- Левое вертикальное меню ----------
        self.menu_widget = QFrame()
        self.menu_widget.setFixedWidth(220)
        self.menu_widget.setStyleSheet("background-color: #F5F5F5; border-right: 1px solid #DDD;")
        menu_layout = QVBoxLayout(self.menu_widget)
        menu_layout.setContentsMargins(5, 10, 5, 10)
        menu_layout.setSpacing(5)
        menu_layout.setAlignment(Qt.AlignTop)

        self.btn_notes = QPushButton("📝 Записи")
        self.btn_cards = QPushButton("🃏 Карточки")
        self.btn_tasks = QPushButton("✅ Задачи")
        self.btn_sessions = QPushButton("⏱ Сессии")
        self.btn_analytics = QPushButton("📊 Аналитика")

        menu_style = """
            QPushButton {
                text-align: left;
                padding: 10px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """
        for btn in [self.btn_notes, self.btn_cards, self.btn_tasks, self.btn_sessions, self.btn_analytics]:
            btn.setStyleSheet(menu_style)
            btn.setMinimumHeight(40)
            menu_layout.addWidget(btn)

        menu_layout.addStretch()
        content_layout.addWidget(self.menu_widget)

        # ---------- Правая область (QStackedWidget) ----------
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack, 1)

        # ---------------------------------------------------------
        # Страница 0: Записи (главная страница записей темы)
        # ---------------------------------------------------------
        notes_main_page = self._create_notes_main_page()
        self.stack.addWidget(notes_main_page)  # индекс 0

        # ---------------------------------------------------------
        # Страница 1: Просмотр одной записи (режим чтения)
        # ---------------------------------------------------------
        self.read_view_page = self._create_read_view_page()
        self.stack.addWidget(self.read_view_page)  # индекс 1

        # ---------------------------------------------------------
        # Страница 2: Редактирование записи (режим редактирования)
        # ---------------------------------------------------------
        self.edit_view_page = self._create_edit_view_page()
        self.stack.addWidget(self.edit_view_page)  # индекс 2

        # ---------------------------------------------------------
        # Карточки, Задачи, Сессии, Аналитика (пока заглушки)
        # ---------------------------------------------------------
        cards_widget = QLabel("🃏 Здесь будут карточки\n\nСкоро появится функционал создания карточек из заметок")
        cards_widget.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(cards_widget)  # индекс 3

        tasks_widget = QLabel("✅ Здесь будут задачи\n\nСписок задач с дедлайнами появится позже")
        tasks_widget.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(tasks_widget)  # индекс 4

        sessions_widget = QLabel("⏱ Здесь будут сессии\n\nТрекер времени и концентрации появится позже")
        sessions_widget.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(sessions_widget)  # индекс 5

        analytics_widget = QLabel("📊 Здесь будет аналитика\n\nГрафики и статистика появятся позже")
        analytics_widget.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(analytics_widget)  # индекс 6

        # Подключаем кнопки меню
        self.btn_notes.clicked.connect(lambda: self._switch_to_notes_main())
        self.btn_cards.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        self.btn_tasks.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        self.btn_sessions.clicked.connect(lambda: self.stack.setCurrentIndex(5))
        self.btn_analytics.clicked.connect(lambda: self.stack.setCurrentIndex(6))

        # Инициализация
        self.current_note_id = None
        self.all_notes = []  # для поиска
        self._load_notes_list()

    # ==================== СОЗДАНИЕ СТРАНИЦ ====================

    def _create_notes_main_page(self) -> QWidget:
        """Страница со списком всех записей темы (с переключателем вида и сортировкой)."""
        page = QWidget()
        layout = QVBoxLayout(page)

        # ========== Верхняя панель: поиск + кнопка новой записи ==========
        top_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск по записям...")
        self.search_input.textChanged.connect(self._filter_notes)
        top_row.addWidget(self.search_input)

        self.btn_new_note = QPushButton("+ Новая запись")
        self.btn_new_note.clicked.connect(self._create_new_note)
        top_row.addWidget(self.btn_new_note)
        layout.addLayout(top_row)

        # ========== Панель управления: вид + сортировка ==========
        control_row = QHBoxLayout()

        # Переключатель вида (плитки / список)
        self.btn_list_view = QPushButton("📋 Список")
        self.btn_grid_view = QPushButton("📱 Плитки")
        self.btn_list_view.setCheckable(True)
        self.btn_grid_view.setCheckable(True)
        self.btn_list_view.setChecked(True)  # по умолчанию список

        self.btn_list_view.clicked.connect(lambda: self._set_view_mode("list"))
        self.btn_grid_view.clicked.connect(lambda: self._set_view_mode("grid"))

        control_row.addWidget(self.btn_list_view)
        control_row.addWidget(self.btn_grid_view)
        control_row.addSpacing(20)

        # Сортировка
        sort_label = QLabel("Сортировать:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("📅 По дате изменения")
        self.sort_combo.addItem("🔤 По алфавиту")
        self.sort_combo.currentIndexChanged.connect(self._apply_sorting)

        control_row.addWidget(sort_label)
        control_row.addWidget(self.sort_combo)
        control_row.addStretch()

        layout.addLayout(control_row)

        # ========== Контейнер для отображения записей ==========
        self.notes_container = QWidget()
        self.notes_layout = QVBoxLayout(self.notes_container)
        self.notes_layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.notes_container)

        return page

    def _create_read_view_page(self) -> QWidget:
        """Страница просмотра записи (режим чтения)."""
        page = QWidget()
        layout = QVBoxLayout(page)

        # Верхняя панель: кнопка "Назад к записям" + кнопка "Редактировать"
        top_bar = QHBoxLayout()
        self.back_to_notes_btn = QPushButton("← Назад к записям")
        self.back_to_notes_btn.clicked.connect(lambda: self._switch_to_notes_main())
        top_bar.addWidget(self.back_to_notes_btn)

        top_bar.addStretch()

        self.edit_note_btn = QPushButton("✏️ Редактировать")
        self.edit_note_btn.clicked.connect(self._switch_to_edit_mode)
        top_bar.addWidget(self.edit_note_btn)

        layout.addLayout(top_bar)

        # Заголовок записи
        self.read_title_label = QLabel()
        self.read_title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.read_title_label)

        # Текст записи (read-only)
        self.read_content_label = QLabel()
        self.read_content_label.setWordWrap(True)
        self.read_content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.read_content_label.setStyleSheet("font-size: 14px; margin-top: 10px;")
        layout.addWidget(self.read_content_label)

        layout.addStretch()

        return page

    def _create_edit_view_page(self) -> QWidget:
        """Страница редактирования записи (режим редактирования)."""
        page = QWidget()
        layout = QVBoxLayout(page)

        # Верхняя панель: кнопка "Назад к записи" + кнопка "Сохранить"
        top_bar = QHBoxLayout()
        self.back_to_read_btn = QPushButton("← Назад к записи")
        self.back_to_read_btn.clicked.connect(self._switch_to_read_mode)
        top_bar.addWidget(self.back_to_read_btn)

        top_bar.addStretch()

        self.save_note_btn = QPushButton("💾 Сохранить")
        self.save_note_btn.clicked.connect(self._save_and_go_back)
        top_bar.addWidget(self.save_note_btn)

        layout.addLayout(top_bar)

        # Редактор
        self.edit_editor = QTextEdit()
        layout.addWidget(self.edit_editor)

        return page

    # ==================== НАВИГАЦИЯ МЕЖДУ РЕЖИМАМИ ====================

    def _switch_to_notes_main(self):
        """Возврат к списку записей темы."""
        self.search_input.clear()
        self._load_notes_list()
        self.stack.setCurrentIndex(0)

    def _switch_to_read_mode(self):
        """Переход из редактирования в режим чтения (с сохранением)."""
        self._save_current_note_from_editor()
        self._update_read_view()
        self.stack.setCurrentIndex(1)

    def _switch_to_edit_mode(self):
        """Переход из режима чтения в режим редактирования."""
        self._load_note_to_editor()
        self.stack.setCurrentIndex(2)

    def _save_and_go_back(self):
        """Сохраняет заметку и возвращается в режим чтения."""
        self._save_current_note_from_editor()
        self._update_read_view()
        self.stack.setCurrentIndex(1)

    # ==================== РАБОТА СО СПИСКОМ ЗАПИСЕЙ (С ПОИСКОМ) ====================

    def _load_notes_list(self):
        self.all_notes = self.note_controller.get_notes_by_topic(self.topic_id)
        self.all_notes_filtered = self.all_notes.copy()
        self._apply_sorting()

    def _filter_notes(self, text: str):
        """Фильтрует записи по тексту поиска и применяет сортировку."""
        if not text.strip():
            self.all_notes_filtered = self.all_notes.copy()
        else:
            text_lower = text.lower()
            filtered = []
            for note in self.all_notes:
                title = (note.title or "").lower()
                content = (note.content or "").lower()
                if text_lower in title or text_lower in content:
                    filtered.append(note)
            self.all_notes_filtered = filtered

        self._apply_sorting()

    def _set_view_mode(self, mode: str):
        self.current_view_mode = mode
        self.btn_list_view.setChecked(mode == "list")
        self.btn_grid_view.setChecked(mode == "grid")
        self._display_notes(
            self.all_notes_filtered if hasattr(self, 'all_notes_filtered') else [])  # перестроить с текущей сортировкой

    def _apply_sorting(self):
        """Применяет текущую сортировку и обновляет отображение."""
        if not hasattr(self, 'all_notes_filtered'):
            self.all_notes_filtered = self.all_notes.copy()

        # Сортировка
        if self.sort_combo.currentIndex() == 0:  # по дате
            self.all_notes_filtered.sort(key=lambda x: x.updated_at or "", reverse=True)
        else:  # по алфавиту
            self.all_notes_filtered.sort(key=lambda x: (x.title or "").lower())

        # Отображение
        self._display_notes(self.all_notes_filtered)

    def _display_notes(self, notes):
        """Полностью перерисовывает контейнер с заметками."""

        # 1. Полностью очищаем контейнер (удаляем всё)
        while self.notes_layout.count():
            item = self.notes_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                # Очищаем вложенные лэйауты (например, grid)
                self._clear_layout(item.layout())

        if not notes:
            empty_label = QLabel("Нет записей. Создайте первую запись!")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: gray; padding: 40px;")
            self.notes_layout.addWidget(empty_label)
            return

        if self.current_view_mode == "list":
            # Список: вертикальные карточки
            for note in notes:
                card = self._create_note_card_list(note)
                self.notes_layout.addWidget(card)
        else:
            # Плитки: сетка 3 колонки
            grid = QGridLayout()
            grid.setSpacing(15)
            grid.setContentsMargins(0, 0, 0, 0)
            row, col = 0, 0
            for note in notes:
                card = self._create_note_card_grid(note)
                grid.addWidget(card, row, col)
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
            self.notes_layout.addLayout(grid)

    def _clear_layout(self, layout):
        """Рекурсивно очищает layout и удаляет все виджеты."""
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self._clear_layout(item.layout())

    def _create_note_card_list(self, note):
        """Создаёт карточку заметки для режима списка."""
        card = QFrame()
        card.setFrameShape(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                border: 1px solid #DDD;
                border-radius: 6px;
                padding: 8px;
                margin: 2px;
                background-color: white;
            }
            QFrame:hover {
                background-color: #F9F9F9;
                border-color: #AAA;
            }
        """)
        card.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(card)

        title = note.title if note.title else "Без названия"
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)

        if note.updated_at:
            date_label = QLabel(f"📅 {note.updated_at[:16]}")
            date_label.setStyleSheet("color: gray; font-size: 10px;")
            layout.addWidget(date_label)

        # Превью текста (первые 100 символов)
        if note.content:
            preview = note.content[:100].replace("\n", " ")
            preview_label = QLabel(preview)
            preview_label.setStyleSheet("color: #555; font-size: 12px;")
            preview_label.setWordWrap(True)
            layout.addWidget(preview_label)

        card.mousePressEvent = lambda e, nid=note.id: self._open_note_read_by_id(nid)

        return card

    def _create_note_card_grid(self, note):
        """Создаёт карточку заметки для режима плиток."""
        card = QFrame()
        card.setFrameShape(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                border: 1px solid #DDD;
                border-radius: 8px;
                padding: 12px;
                background-color: white;
                min-height: 120px;
            }
            QFrame:hover {
                background-color: #F9F9F9;
                border-color: #AAA;
            }
        """)
        card.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(card)

        title = note.title if note.title else "Без названия"
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        if note.updated_at:
            date_label = QLabel(f"📅 {note.updated_at[:16]}")
            date_label.setStyleSheet("color: gray; font-size: 10px;")
            layout.addWidget(date_label)

        layout.addStretch()

        card.mousePressEvent = lambda e, nid=note.id: self._open_note_read_by_id(nid)

        return card

    def _open_note_read_by_id(self, note_id: int):
        """Открывает заметку по id в режиме чтения."""
        self.current_note_id = note_id
        self._update_read_view()
        self.stack.setCurrentIndex(1)

    def _open_note_read(self, item: QListWidgetItem):
        """Открывает выбранную запись в режиме чтения."""
        note_id = item.data(Qt.UserRole)
        if note_id:
            self.current_note_id = note_id
            self._update_read_view()
            self.stack.setCurrentIndex(1)

    def _update_read_view(self):
        """Обновляет страницу чтения данными текущей заметки."""
        note = self.note_controller.get_note(self.current_note_id)
        if note:
            self.read_title_label.setText(note.title if note.title else "Без названия")
            self.read_content_label.setText(note.content if note.content else "")

    def _load_note_to_editor(self):
        """Загружает текущую заметку в редактор."""
        note = self.note_controller.get_note(self.current_note_id)
        if note:
            self.edit_editor.setPlainText(note.content if note.content else "")

    def _save_current_note_from_editor(self):
        """Сохраняет содержимое редактора в БД."""
        if not self.current_note_id:
            return
        content = self.edit_editor.toPlainText()
        self.note_controller.update_note(self.current_note_id, content=content)

    # ==================== КОНТЕКСТНОЕ МЕНЮ ДЛЯ ЗАПИСЕЙ ====================

    def _open_note_context_menu(self, pos):
        item = self.notes_list.itemAt(pos)
        if not item:
            return
        note_id = item.data(Qt.UserRole)
        if not note_id:
            return

        menu = QMenu(self)
        rename_action = QAction("Переименовать", self)
        delete_action = QAction("Удалить", self)
        menu.addAction(rename_action)
        menu.addAction(delete_action)

        rename_action.triggered.connect(lambda: self._rename_note(note_id, item))
        delete_action.triggered.connect(lambda: self._delete_note(note_id))

        menu.exec(self.notes_list.mapToGlobal(pos))

    def _rename_note(self, note_id: int, item: QListWidgetItem):
        new_title, ok = QInputDialog.getText(self, "Переименовать", "Новое название записи:")
        if ok and new_title.strip():
            self.note_controller.update_note(note_id, title=new_title.strip())
            self._load_notes_list()

    def _delete_note(self, note_id: int):
        reply = QMessageBox.question(
            self, "Удалить запись",
            "Вы уверены, что хотите удалить эту запись?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.note_controller.delete_note(note_id)
            if self.current_note_id == note_id:
                self.current_note_id = None
            self._load_notes_list()
            self._switch_to_notes_main()

    def _create_new_note(self):
        """Создаёт новую запись и открывает её в режиме редактирования."""
        title, ok = QInputDialog.getText(self, "Новая запись", "Введите название записи:")
        if not ok or not title.strip():
            title = "Новая запись"

        note_id = self.note_controller.create_note(self.topic_id, title.strip(), "")
        self.current_note_id = note_id
        self._load_notes_list()

        # Открываем в режиме редактирования
        self.edit_editor.setPlainText("")
        self.stack.setCurrentIndex(2)
