import sys
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow

# Если хочешь подключить тему — раскомментируй
# from utils.theme_manager import ThemeManager


def main():
    app = QApplication(sys.argv)

    # -----------------------------------------
    # Тема оформления (опционально)
    # -----------------------------------------
    # theme = ThemeManager()
    # theme.apply_light_theme()   # или apply_dark_theme()

    # -----------------------------------------
    # Главное окно
    # -----------------------------------------
    window = MainWindow()
    window.show()

    # -----------------------------------------
    # Запуск приложения
    # -----------------------------------------
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
