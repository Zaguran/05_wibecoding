import os
import tempfile
import pytest
import todo_store


@pytest.fixture(autouse=True)
def tmp_db(monkeypatch, tmp_path):
    """Každý test dostane prázdnou dočasnou databázi."""
    db = str(tmp_path / "test.db")
    monkeypatch.setattr(todo_store, "DB_PATH", db)
    # Přepíšeme i import v modulu
    import config
    monkeypatch.setattr(config, "DB_PATH", db)
    todo_store.init_db()
    yield


def test_add_and_list():
    todo_id = todo_store.add("Koupit mléko")
    todos = todo_store.list_todos()
    assert len(todos) == 1
    assert todos[0]["id"] == todo_id
    assert todos[0]["title"] == "Koupit mléko"
    assert todos[0]["done"] == 0


def test_complete():
    todo_id = todo_store.add("Napsat testy")
    assert todo_store.complete(todo_id) is True
    todos = todo_store.list_todos(show_done=False)
    assert len(todos) == 0
    todos_all = todo_store.list_todos(show_done=True)
    assert todos_all[0]["done"] == 1


def test_complete_nonexistent():
    assert todo_store.complete(999) is False


def test_delete():
    todo_id = todo_store.add("Smazat mě")
    assert todo_store.delete(todo_id) is True
    assert len(todo_store.list_todos(show_done=True)) == 0


def test_delete_nonexistent():
    assert todo_store.delete(999) is False


def test_due_today():
    from datetime import datetime
    today = datetime.now().date().isoformat()
    todo_store.add("Dnes splatný", due=today)
    todo_store.add("Bez deadline")
    due = todo_store.due_today()
    assert len(due) == 1
    assert due[0]["title"] == "Dnes splatný"


def test_due_today_excludes_done():
    from datetime import datetime
    today = datetime.now().date().isoformat()
    tid = todo_store.add("Hotový dnes", due=today)
    todo_store.complete(tid)
    assert len(todo_store.due_today()) == 0
