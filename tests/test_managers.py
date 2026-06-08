from utils.import_manager import ImportManager
from utils.export_manager import ExportManager

def test_import_export_note(tmp_path):
    imp = ImportManager()
    exp = ExportManager()

    # создаём временный файл
    file = tmp_path / "note.txt"
    file.write_text("Тестовая заметка", encoding="utf-8")

    note_id = imp.import_file(str(file), topic_id=1)
    assert note_id is not None

    out = exp.export_note(note_id, tmp_path)
    assert out.exists()
