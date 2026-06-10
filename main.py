# main.py
import sys
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow
from controllers.topic_controller import TopicController
from controllers.note_controller import NoteController
from controllers.flashcard_controller import FlashcardController
from controllers.task_controller import TaskController
from controllers.session_controller import SessionController

import os
print("Текущая папка:", os.getcwd())
print("Файлы .db:", [f for f in os.listdir('.') if f.endswith('.db')])

def main():
    app = QApplication(sys.argv)

    # Создаём все контроллеры
    topic_controller = TopicController()
    note_controller = NoteController()
    flashcard_controller = FlashcardController()
    task_controller = TaskController()
    session_controller = SessionController()

    # Передаём их в главное окно
    window = MainWindow(
        topic_controller=topic_controller,
        note_controller=note_controller,
        flashcard_controller=flashcard_controller,
        task_controller=task_controller,
        session_controller=session_controller
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()