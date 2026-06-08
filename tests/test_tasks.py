from controllers.task_controller import TaskController

def test_create_task():
    c = TaskController()
    tid = c.create_task("Сделать", "Описание", 1)
    task = c.get_task(tid)
    assert task.title == "Сделать"

def test_mark_done():
    c = TaskController()
    tid = c.create_task("A", "B", 1)
    c.set_status(tid, "done")
    assert c.get_task(tid).status == "done"
