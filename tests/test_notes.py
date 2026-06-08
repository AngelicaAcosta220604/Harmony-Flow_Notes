from controllers.note_controller import NoteController

def test_create_note():
    c = NoteController()
    note_id = c.create_note(topic_id=1, title="Тест", content="Привет")
    note = c.get_note(note_id)
    assert note.title == "Тест"
    assert note.content == "Привет"

def test_update_note():
    c = NoteController()
    nid = c.create_note(1, "A", "B")
    c.update_note(nid, "C", "D")
    note = c.get_note(nid)
    assert note.title == "C"
    assert note.content == "D"
