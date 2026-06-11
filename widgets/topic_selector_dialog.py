# widgets/topic_selector_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QMessageBox
)


class TopicSelectorDialog(QDialog):
    """Диалог выбора темы для создания карточки в глобальном режиме"""

    def __init__(self, topic_controller, parent=None):
        super().__init__(parent)
        self.topic_controller = topic_controller
        self.selected_topic_id = None

        self.setWindowTitle("Выбор темы")
        self.setMinimumWidth(400)
        self.setup_ui()
        self.load_topics()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Выберите тему для новой карточки:"))

        self.topic_combo = QComboBox()
        layout.addWidget(self.topic_combo)

        layout.addSpacing(20)

        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("Создать")
        self.btn_cancel = QPushButton("Отмена")

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def load_topics(self):
        """Загружает темы в комбобокс"""
        topics = self.topic_controller.get_all_topics()
        self.topic_combo.clear()

        for topic in topics:
            if topic.type == "topic":
                self.topic_combo.addItem(f"📄 {topic.name}", topic.id)

        if self.topic_combo.count() == 0:
            QMessageBox.warning(self, "Нет тем", "Сначала создайте хотя бы одну тему!")
            self.reject()

    def get_selected_topic_id(self):
        return self.topic_combo.currentData()