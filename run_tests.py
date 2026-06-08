import pytest
import sys
import os

def run_tests():
    print("\n🚀 Запуск всех тестов Harmony&Flow...\n")

    # абсолютный путь к папке tests
    tests_dir = os.path.join(os.path.dirname(__file__), "tests")

    args = [
        "-v",
        "--color=yes",
        "--maxfail=1",
        tests_dir
    ]

    exit_code = pytest.main(args)

    print("\n🎉 Тестирование завершено!")
    if exit_code == 0:
        print("✔ Все тесты прошли успешно!")
    else:
        print(f"❌ Некоторые тесты упали. Код выхода: {exit_code}")

    sys.exit(exit_code)


if __name__ == "__main__":
    run_tests()
