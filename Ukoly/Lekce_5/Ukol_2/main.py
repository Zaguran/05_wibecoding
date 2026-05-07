"""
TODO CLI — správa úkolů z příkazové řádky.

Použití:
  python main.py add "Napsat testy" --due 2026-05-10
  python main.py list
  python main.py list --all
  python main.py done 1
  python main.py delete 2
  python main.py notify
"""

import argparse
import sys

import todo_store
from notifier import send_reminder


def cmd_add(args: argparse.Namespace) -> None:
    todo_id = todo_store.add(args.title, args.due)
    print(f"Přidáno [#{todo_id}]: {args.title}")


def cmd_list(args: argparse.Namespace) -> None:
    todos = todo_store.list_todos(show_done=args.all)
    if not todos:
        print("Žádné úkoly." if args.all else "Žádné nesplněné úkoly.")
        return
    for row in todos:
        status = "x" if row["done"] else " "
        due = f"  (do: {row['due']})" if row["due"] else ""
        print(f"  [{status}] #{row['id']} {row['title']}{due}")


def cmd_done(args: argparse.Namespace) -> None:
    if todo_store.complete(args.id):
        print(f"Hotovo: #{args.id}")
    else:
        print(f"Úkol #{args.id} nenalezen.", file=sys.stderr)
        sys.exit(1)


def cmd_delete(args: argparse.Namespace) -> None:
    if todo_store.delete(args.id):
        print(f"Smazáno: #{args.id}")
    else:
        print(f"Úkol #{args.id} nenalezen.", file=sys.stderr)
        sys.exit(1)


def cmd_notify(_args: argparse.Namespace) -> None:
    todos = todo_store.due_today()
    if not todos:
        print("Dnes žádné úkoly s deadlinem.")
        return
    send_reminder(todos)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TODO správce úkolů")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Přidat úkol")
    p_add.add_argument("title")
    p_add.add_argument("--due", help="Datum splnění (YYYY-MM-DD)")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="Zobrazit úkoly")
    p_list.add_argument("--all", action="store_true", help="Včetně splněných")
    p_list.set_defaults(func=cmd_list)

    p_done = sub.add_parser("done", help="Označit jako splněný")
    p_done.add_argument("id", type=int)
    p_done.set_defaults(func=cmd_done)

    p_del = sub.add_parser("delete", help="Smazat úkol")
    p_del.add_argument("id", type=int)
    p_del.set_defaults(func=cmd_delete)

    p_notify = sub.add_parser("notify", help="Odeslat e-mail s dnešními úkoly")
    p_notify.set_defaults(func=cmd_notify)

    return parser


if __name__ == "__main__":
    todo_store.init_db()
    args = build_parser().parse_args()
    args.func(args)
