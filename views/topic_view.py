# views/topic_view.py


from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton,  QInputDialog,
    QFrame, QStackedWidget, QScrollArea, QSizePolicy,
    QLineEdit, QComboBox  # <-- ОБА ДОЛЖНЫ БЫТЬ ЗДЕСЬ
)
from widgets.silent_message_box import QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from views.note_editor_view import NoteEditorView
from views.flashcards_view import FlashcardsView
from views.tasks_view import TasksView
from views.sessions_view import SessionsView

class TopicView(QWidget):
    back_requested = Signal()
    start_session_requested = Signal(int, str)
    show_session_analytics = Signal(int)
    cards_updated = Signal()
    topic_updated = Signal()  # для обновления списка тем в фокусе

    def __init__(self, topic_id, topic_controller, note_controller,
                 flashcard_controller, task_controller, session_controller, parent=None):
        super().__init__(parent)
        self.topic_id = topic_id
        self.topic_controller = topic_controller
        self.note_controller = note_controller
        self.flashcard_controller = flashcard_controller
        self.task_controller = task_controller
        self.session_controller = session_controller

        # Загружаем тему
        self.topic = self.topic_controller.get_topic(topic_id)

        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # ========== Верхняя панель ==========
        top_bar = QHBoxLayout()
        self.back_button = QPushButton("← Назад к темам")
        self.back_button.setFixedWidth(120)
        self.back_button.clicked.connect(self.back_requested.emit)
        top_bar.addWidget(self.back_button)

        top_bar.addStretch()

        title_label = QLabel(self.topic.name)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        top_bar.addWidget(title_label)

        top_bar.addStretch()

        if hasattr(self.topic, 'updated_at') and self.topic.updated_at:
            date_label = QLabel(f"Изменено: {self.topic.updated_at[:16]}")
            date_label.setStyleSheet("color: gray; font-size: 11px;")
            top_bar.addWidget(date_label)

        main_layout.addLayout(top_bar)

        main_layout.addSpacing(10)

        # ========== Основное содержимое ==========
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        main_layout.addLayout(content_layout)

        # ---------- Левое вертикальное меню ----------
        self.menu_widget = QFrame()
        self.menu_widget.setFixedWidth(180)
        self.menu_widget.setStyleSheet("background-color: #F5F5F5; border-radius: 8px;")
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
                padding: 8px 12px;
                font-size: 13px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """
        for btn in [self.btn_notes, self.btn_cards, self.btn_tasks, self.btn_sessions, self.btn_analytics]:
            btn.setStyleSheet(menu_style)
            btn.setMinimumHeight(36)
            menu_layout.addWidget(btn)

        menu_layout.addStretch()
        content_layout.addWidget(self.menu_widget)

        # ---------- Правая область (QStackedWidget) ----------
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack, 1)

        # ---------------------------------------------------------
        # Страница 0: Записи (список всех записей темы)
        # ---------------------------------------------------------
        notes_main_page = self._create_notes_main_page()
        self.stack.addWidget(notes_main_page)

        # ---------------------------------------------------------
        # Страница 1: Просмотр одной записи (режим чтения)
        # ---------------------------------------------------------
        self.read_view_page = self._create_read_view_page()
        self.stack.addWidget(self.read_view_page)

        # ---------------------------------------------------------
        # Страница 2: Редактирование записи
        # ---------------------------------------------------------
        self.edit_view_page = NoteEditorView(
            note_controller=note_controller,
            flashcard_controller=flashcard_controller,
            task_controller=task_controller
        )
        self.edit_view_page.back_requested.connect(lambda: self.stack.setCurrentIndex(0))
        self.edit_view_page.note_saved.connect(self._on_note_saved)
        self.stack.addWidget(self.edit_view_page)

        # ---------------------------------------------------------
        # Страница 3: Карточки
        # ---------------------------------------------------------
        self.flashcards_view = FlashcardsView(
            flashcard_controller=self.flashcard_controller,
            topic_controller=self.topic_controller,
            topic_id=self.topic_id
        )
        self.flashcards_view.cards_updated.connect(self._on_cards_updated)
        self.stack.addWidget(self.flashcards_view)

        # ---------------------------------------------------------
        # Страница 4: Задачи
        # ---------------------------------------------------------
        self.tasks_view = TasksView(
            task_controller=task_controller,
            topic_id=topic_id
        )
        self.stack.addWidget(self.tasks_view)

        # ---------------------------------------------------------
        # Страница 5: Сессии
        # ---------------------------------------------------------
        self.sessions_view = SessionsView(
            session_controller=session_controller,
            topic_id=topic_id,
            topic_name=self.topic.name,
            parent=self
        )
        self.sessions_view.start_session_requested.connect(self._start_new_session)
        self.stack.addWidget(self.sessions_view)

        # ---------------------------------------------------------
        # Страница 6: Аналитика (заглушка)
        # ---------------------------------------------------------
        analytics_widget = QLabel("📊 Здесь будет аналитика\n\nГрафики и статистика появятся позже")
        analytics_widget.setAlignment(Qt.AlignCenter)
        analytics_widget.setStyleSheet("font-size: 14px; color: #666;")
        self.stack.addWidget(analytics_widget)

        # Подключаем кнопки меню
        self.btn_notes.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_cards.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        self.btn_tasks.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        self.btn_sessions.clicked.connect(lambda: self.stack.setCurrentIndex(5))
        self.btn_analytics.clicked.connect(lambda: self.stack.setCurrentIndex(6))

        # По умолчанию показываем список записей
        self.stack.setCurrentIndex(0)

        # Инициализация
        self.current_note_id = None
        self.all_notes = []
        self._load_notes_list()

    # ==================== СОЗДАНИЕ СТРАНИЦ ====================

    def _create_notes_main_page(self) -> QWidget:
        """Страница со списком всех записей темы (только список, без плиток)"""
        page = QWidget()
        page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # ========== Верхняя панель: поиск + кнопка новой записи ==========
        top_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск по записям...")
        self.search_input.setMinimumHeight(32)
        self.search_input.textChanged.connect(self._filter_notes)
        top_row.addWidget(self.search_input)

        self.btn_new_note = QPushButton("+ Новая запись")
        self.btn_new_note.setFixedHeight(32)
        self.btn_new_note.clicked.connect(self._create_new_note)
        top_row.addWidget(self.btn_new_note)
        layout.addLayout(top_row)

        # ========== Панель сортировки ==========
        control_row = QHBoxLayout()
        sort_label = QLabel("Сортировать:")
        sort_label.setStyleSheet("font-size: 12px;")
        control_row.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.addItem("📅 По дате изменения")
        self.sort_combo.addItem("🔤 По алфавиту")
        self.sort_combo.currentIndexChanged.connect(self._apply_sorting)
        control_row.addWidget(self.sort_combo)
        control_row.addStretch()
        layout.addLayout(control_row)

        layout.addSpacing(5)

        # ========== Область с прокруткой для списка записей ==========
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.notes_container = QWidget()
        self.notes_layout = QVBoxLayout(self.notes_container)
        self.notes_layout.setAlignment(Qt.AlignTop)
        self.notes_layout.setSpacing(8)
        self.notes_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area.setWidget(self.notes_container)
        layout.addWidget(scroll_area)

        return page

    def _create_read_view_page(self) -> QWidget:
        """Страница просмотра записи (режим чтения)"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Верхняя панель
        top_bar = QHBoxLayout()

        self.back_to_notes_btn = QPushButton("← Назад к записям")
        self.back_to_notes_btn.clicked.connect(lambda: self._switch_to_notes_main())
        top_bar.addWidget(self.back_to_notes_btn)

        top_bar.addStretch()

        self.edit_note_btn = QPushButton("✏️ Редактировать")
        self.edit_note_btn.clicked.connect(self._switch_to_edit_mode)
        top_bar.addWidget(self.edit_note_btn)

        layout.addLayout(top_bar)

        # Заголовок
        self.read_title_label = QLabel()
        self.read_title_label.setWordWrap(True)
        self.read_title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.read_title_label)

        # Текст с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.read_content_label = QLabel()
        self.read_content_label.setWordWrap(True)
        self.read_content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.read_content_label.setStyleSheet("font-size: 14px; margin-top: 10px;")
        content_layout.addWidget(self.read_content_label)

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        return page

    def _on_note_saved(self, note_id: int):
        """Обновляет список после сохранения"""
        self._load_notes_list()
        self._update_read_view()

    # ==================== НАВИГАЦИЯ ====================

    def _switch_to_notes_main(self):
        """Возврат к списку записей"""
        self.search_input.clear()
        self._load_notes_list()
        self.stack.setCurrentIndex(0)

    def _switch_to_read_mode(self):
        """Переход из редактирования в режим чтения"""
        if self.current_note_id:
            self._save_current_note_from_editor()
            self._update_read_view()
            self.stack.setCurrentIndex(1)

    def _switch_to_edit_mode(self):
        """Переход из режима чтения в режим редактирования"""
        if self.current_note_id:
            self.edit_view_page.load_note(self.current_note_id, self.topic_id)
            self.stack.setCurrentIndex(2)

    def _save_and_go_back(self):
        """Сохраняет заметку и возвращается в режим чтения"""
        self._save_current_note_from_editor()
        self._update_read_view()
        self.stack.setCurrentIndex(1)

    # ==================== РАБОТА СО СПИСКОМ ЗАПИСЕЙ ====================

    def _load_notes_list(self):
        self.all_notes = self.note_controller.get_notes_by_topic(self.topic_id)
        self.all_notes_filtered = self.all_notes.copy()
        self._apply_sorting()

    def _filter_notes(self, text: str):
        """Фильтрует записи по тексту поиска"""
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

    def _apply_sorting(self):
        """Применяет сортировку и обновляет отображение"""
        if not hasattr(self, 'all_notes_filtered'):
            self.all_notes_filtered = self.all_notes.copy()

        if self.sort_combo.currentIndex() == 0:
            self.all_notes_filtered.sort(key=lambda x: x.updated_at or "", reverse=True)
        else:
            self.all_notes_filtered.sort(key=lambda x: (x.title or "").lower())

        self._display_notes(self.all_notes_filtered)

    def _display_notes(self, notes):
        """Отображает список заметок"""
        # Очищаем контейнер
        while self.notes_layout.count():
            item = self.notes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not notes:
            empty_label = QLabel("Нет записей. Создайте первую запись!")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: gray; padding: 40px;")
            self.notes_layout.addWidget(empty_label)
            return

        for note in notes:
            card = self._create_note_card(note)
            self.notes_layout.addWidget(card)

    def _create_note_card(self, note):
        """Создаёт карточку заметки для списка"""
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

        layout = QVBoxLayout(card)
        layout.setSpacing(5)

        # Верхняя строка: название + кнопки
        header_layout = QHBoxLayout()

        title = note.title if note.title else "Без названия"
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        title_label.setCursor(Qt.PointingHandCursor)
        title_label.mousePressEvent = lambda e, nid=note.id: self._open_note_read_by_id(nid)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Кнопка переименования
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(24, 24)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFC107;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #FFB300; }
        """)
        edit_btn.setToolTip("Переименовать")
        edit_btn.clicked.connect(lambda checked=False, nid=note.id, t=title: self._rename_note(nid, t))
        header_layout.addWidget(edit_btn)

        # Кнопка удаления
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(24, 24)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                border: none;
                border-radius: 4px;
                font-size: 11px;
                color: white;
            }
            QPushButton:hover { background-color: #D32F2F; }
        """)
        delete_btn.setToolTip("Удалить")
        delete_btn.clicked.connect(lambda checked=False, nid=note.id: self._delete_note(nid))
        header_layout.addWidget(delete_btn)

        layout.addLayout(header_layout)

        # Дата
        if note.updated_at:
            date_label = QLabel(note.updated_at[:16])
            date_label.setStyleSheet("color: gray; font-size: 10px;")
            layout.addWidget(date_label)

        # Превью текста
        if note.content:
            preview = note.content[:150].replace("\n", " ")
            preview_label = QLabel(preview)
            preview_label.setStyleSheet("color: #555; font-size: 12px;")
            preview_label.setWordWrap(True)
            layout.addWidget(preview_label)

        return card

    def _open_note_read_by_id(self, note_id: int):
        """Открывает заметку по id в режиме чтения"""
        self.current_note_id = note_id
        self._update_read_view()
        self.stack.setCurrentIndex(1)

    def _update_read_view(self):
        """Обновляет страницу чтения данными текущей заметки"""
        note = self.note_controller.get_note(self.current_note_id)
        if note:
            self.read_title_label.setText(note.title if note.title else "Без названия")
            self.read_content_label.setText(note.content if note.content else "")

    def _save_current_note_from_editor(self):
        """Сохраняет содержимое редактора в БД"""
        if not self.current_note_id:
            return
        content = self.edit_editor.toPlainText()
        self.note_controller.update_note(self.current_note_id, content=content)

    # ==================== ОПЕРАЦИИ С ЗАПИСЯМИ ====================

    def _rename_note(self, note_id: int, old_title: str):
        """Переименовывает заметку"""
        new_title, ok = QInputDialog.getText(self, "Переименовать", "Новое название записи:", text=old_title)
        if ok and new_title.strip():
            self.note_controller.update_note(note_id, title=new_title.strip())
            self._load_notes_list()
            self.topic_updated.emit()
            if self.current_note_id == note_id:
                self._update_read_view()

    def _delete_note(self, note_id: int):
        """Удаляет заметку"""
        reply = QMessageBox.question(
            self, "Удалить запись",
            "Вы уверены, что хотите удалить эту запись?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.note_controller.delete_note(note_id)
            self.topic_updated.emit()
            if self.current_note_id == note_id:
                self.current_note_id = None
                self._switch_to_notes_main()
            else:
                self._load_notes_list()

    def _create_new_note(self):
        """Создаёт новую запись и открывает её в режиме редактирования"""
        title, ok = QInputDialog.getText(self, "Новая запись", "Введите название записи:")

        if not ok:
            return

        if not title.strip():
            QMessageBox.warning(self, "Ошибка", "Название записи не может быть пустым!")
            return

        note_id = self.note_controller.create_note(self.topic_id, title.strip(), "")
        self.topic_updated.emit()
        self.current_note_id = note_id
        self.edit_view_page.load_note(note_id, self.topic_id)
        self._load_notes_list()
        self.stack.setCurrentIndex(2)

    # ==================== СЕССИИ И КАРТОЧКИ ====================

    def _start_new_session(self, topic_id: int, topic_name: str):
        """Запускает новую сессию для темы"""
        self.start_session_requested.emit(topic_id, topic_name)

    def _on_cards_updated(self):
        """Пробрасывает сигнал обновления карточек наверх"""
        self.cards_updated.emit()
        self.topic_updated.emit()

    # ==================== ЗАГЛУШКИ ДЛЯ ОТСУТСТВУЮЩИХ МЕТОДОВ ====================

    def _edit_editor(self):
        """Заглушка для редактора (используется NoteEditorView)"""
        pass