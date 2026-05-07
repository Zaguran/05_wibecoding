"""
Lekce 5, Úkol AgenticEngineering 1 — Loop pattern (dynamická fronta)

Workflow:
  Agent dostane vysokoúrovňový úkol. V každé iteraci smyčky rozhodne:
    - decompose_task → rozloží úkol na 2–4 podúkoly, přidá je do fronty
    - execute_task   → úkol je dost malý, provede ho a označí jako hotový

  Smyčka běží dokud není fronta prázdná nebo není dosažen MAX_ITERATIONS.
  Stav (fronta, výsledky) je uložen v SQLite přes todo_store.py.

Požadavky:
  pip install anthropic python-dotenv
  export ANTHROPIC_API_KEY=...
"""

import json
import os

import anthropic
from dotenv import load_dotenv

import todo_store

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
MAX_ITERATIONS = 20
MAX_DEPTH = 3  # maximální hloubka rozkladu


# ---------------------------------------------------------------------------
# Nástroje agenta
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "decompose_task",
        "description": (
            "Použij pokud je úkol příliš velký nebo vágní. "
            "Rozloží ho na 2–4 konkrétní, realizovatelné podúkoly."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "subtasks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Seznam podúkolů (2–4 položky)",
                    "minItems": 2,
                    "maxItems": 4,
                }
            },
            "required": ["subtasks"],
        },
    },
    {
        "name": "execute_task",
        "description": (
            "Použij pokud je úkol dost konkrétní a malý na přímé provedení. "
            "Popiš co bylo uděláno."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "string",
                    "description": "Stručný popis provedeného výstupu",
                }
            },
            "required": ["result"],
        },
    },
]


# ---------------------------------------------------------------------------
# Agent — jedno rozhodnutí pro jeden úkol
# ---------------------------------------------------------------------------

def process_task(title: str, depth: int) -> dict:
    """
    Volá agenta s nástrojem decompose_task nebo execute_task.
    Vrátí {'action': 'decompose'|'execute', 'subtasks'|'result': ...}
    """
    depth_note = (
        f" (hloubka rozkladu: {depth}/{MAX_DEPTH} — MUSÍŠ použít execute_task)"
        if depth >= MAX_DEPTH
        else ""
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        tools=TOOLS,
        tool_choice={"type": "any"},
        messages=[
            {
                "role": "user",
                "content": (
                    f"Úkol: {title}{depth_note}\n\n"
                    "Je tento úkol dost konkrétní na přímé provedení, "
                    "nebo ho musíš nejdříve rozložit na podúkoly?\n"
                    "Použij právě jeden nástroj."
                ),
            }
        ],
    )

    for block in response.content:
        if block.type == "tool_use":
            if block.name == "decompose_task":
                return {"action": "decompose", "subtasks": block.input["subtasks"]}
            if block.name == "execute_task":
                return {"action": "execute", "result": block.input["result"]}

    # Fallback — agent nepoužil nástroj
    return {"action": "execute", "result": "(agent neodpověděl nástrojem)"}


# ---------------------------------------------------------------------------
# Orchestrátor — dynamická smyčka
# ---------------------------------------------------------------------------

def run_loop(initial_task: str) -> None:
    """
    Hlavní smyčka. Fronta je seznam tuplů (todo_id, title, depth).
    """
    todo_store.init_db()

    # Zaznamenáme počáteční úkol do DB
    root_id = todo_store.add(initial_task)
    queue: list[tuple[int, str, int]] = [(root_id, initial_task, 0)]

    print(f"\n{'='*60}")
    print(f"LOOP START: {initial_task}")
    print(f"{'='*60}\n")

    iteration = 0
    results: list[dict] = []

    while queue and iteration < MAX_ITERATIONS:
        iteration += 1
        todo_id, title, depth = queue.pop(0)

        print(f"[Iterace {iteration:02d}] {'  ' * depth}▶ {title}")

        decision = process_task(title, depth)

        if decision["action"] == "decompose":
            subtasks = decision["subtasks"]
            print(f"{'  ' * depth}  → rozloženo na {len(subtasks)} podúkolů:")
            for sub in subtasks:
                sub_id = todo_store.add(sub)
                queue.append((sub_id, sub, depth + 1))
                print(f"{'  ' * depth}    • {sub}")
            # Rodičovský úkol označíme jako hotový (byl nahrazen podúkoly)
            todo_store.complete(todo_id)

        else:  # execute
            result = decision["result"]
            todo_store.complete(todo_id)
            results.append({"task": title, "result": result, "depth": depth})
            print(f"{'  ' * depth}  ✓ {result}")

        print()

    # Shrnutí
    print(f"{'='*60}")
    print(f"HOTOVO — {iteration} iterací, {len(results)} úkolů provedeno\n")
    print("PROVEDENÉ ÚKOLY:")
    for r in results:
        indent = "  " * r["depth"]
        print(f"{indent}✓ {r['task']}")
        print(f"{indent}  → {r['result']}")
    print(f"{'='*60}\n")

    # Uložíme report
    with open("loop_report.md", "w", encoding="utf-8") as f:
        f.write(f"# Loop report: {initial_task}\n\n")
        f.write(f"Iterací: {iteration}, provedených úkolů: {len(results)}\n\n")
        f.write("## Výsledky\n\n")
        for r in results:
            f.write(f"- **{r['task']}**  \n  {r['result']}\n\n")
    print("Report uložen do loop_report.md")


# ---------------------------------------------------------------------------
# Vstupní bod
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Chybí ANTHROPIC_API_KEY — nastav ho v .env nebo jako env proměnnou.")
        raise SystemExit(1)

    # Vysokoúrovňový úkol — agent ho bude rekurzivně rozkládat
    run_loop("Vytvořit webovou aplikaci pro správu projektů")
