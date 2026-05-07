import sqlite3
from datetime import datetime
from config import DB_PATH


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                title     TEXT    NOT NULL,
                done      INTEGER NOT NULL DEFAULT 0,
                due       TEXT,
                created   TEXT    NOT NULL
            )
        """)


def add(title: str, due: str | None = None) -> int:
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO todos (title, due, created) VALUES (?, ?, ?)",
            (title, due, datetime.now().isoformat()),
        )
        return cur.lastrowid


def list_todos(show_done: bool = False) -> list[sqlite3.Row]:
    with _connect() as conn:
        if show_done:
            return conn.execute("SELECT * FROM todos ORDER BY id").fetchall()
        return conn.execute(
            "SELECT * FROM todos WHERE done = 0 ORDER BY id"
        ).fetchall()


def complete(todo_id: int) -> bool:
    with _connect() as conn:
        cur = conn.execute(
            "UPDATE todos SET done = 1 WHERE id = ?", (todo_id,)
        )
        return cur.rowcount > 0


def delete(todo_id: int) -> bool:
    with _connect() as conn:
        cur = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        return cur.rowcount > 0


def due_today() -> list[sqlite3.Row]:
    today = datetime.now().date().isoformat()
    with _connect() as conn:
        return conn.execute(
            "SELECT * FROM todos WHERE done = 0 AND due = ?", (today,)
        ).fetchall()
