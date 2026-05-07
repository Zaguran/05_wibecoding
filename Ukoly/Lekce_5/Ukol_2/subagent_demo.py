"""
Lekce 5, Úkol 2 — Ukázka orchestrace subagentů s Anthropic SDK

Workflow (sekvenční + paralelní):
  1. [Explore agent]   — prohledá kód a najde Python soubory
  2. [Plan agent]      — navrhne, jak kód vylepšit (paralelně pro každý soubor)
  3. [Review agent]    — shrne výsledky plánů do finálního reportu

Požadavky:
  pip install anthropic python-dotenv
  export ANTHROPIC_API_KEY=...
"""

import asyncio
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")


# ---------------------------------------------------------------------------
# Pomocné funkce
# ---------------------------------------------------------------------------

def run_agent(system: str, user: str, max_tokens: int = 1024) -> str:
    """Spustí jednoduchého agenta a vrátí jeho textovou odpověď."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text


# ---------------------------------------------------------------------------
# Subagenti
# ---------------------------------------------------------------------------

def explore_agent(codebase_description: str) -> list[dict]:
    """
    Explore subagent — analyzuje popis projektu a identifikuje klíčové soubory.
    V reálném nasazení by měl přístup k nástrojům Read/Bash.
    """
    print("  [Explore] Hledám soubory a symboly...")
    result = run_agent(
        system=(
            "Jsi Explore agent. Analyzuješ strukturu Python projektu. "
            "Vždy odpovíš jako JSON seznam objektů s klíči 'file' a 'purpose'."
        ),
        user=(
            f"Projekt:\n{codebase_description}\n\n"
            "Identifikuj klíčové Python soubory a jejich účel. "
            "Odpověz POUZE jako JSON seznam, např.: "
            '[{"file": "main.py", "purpose": "vstupní bod"}, ...]'
        ),
    )

    import json
    import re

    # Extrahujeme JSON i pokud model obalí odpověď textem
    match = re.search(r"\[.*\]", result, re.DOTALL)
    if match:
        return json.loads(match.group())
    return [{"file": "unknown", "purpose": result}]


def plan_agent(file_info: dict) -> dict:
    """
    Plan subagent — pro jeden soubor navrhne konkrétní vylepšení.
    """
    print(f"  [Plan] Navrhuji vylepšení pro {file_info['file']}...")
    suggestion = run_agent(
        system=(
            "Jsi Plan agent. Navrhuješ konkrétní, realizovatelná vylepšení kódu. "
            "Buď stručný — max 3 body."
        ),
        user=(
            f"Soubor: {file_info['file']}\n"
            f"Účel: {file_info['purpose']}\n\n"
            "Navrhni 3 konkrétní vylepšení tohoto souboru z pohledu kvality kódu, "
            "výkonu nebo bezpečnosti."
        ),
    )
    return {"file": file_info["file"], "suggestions": suggestion}


def review_agent(plans: list[dict]) -> str:
    """
    Review subagent — agreguje výstupy Plan agentů do finálního reportu.
    """
    print("  [Review] Sestavuji finální report...")
    plans_text = "\n\n".join(
        f"### {p['file']}\n{p['suggestions']}" for p in plans
    )
    return run_agent(
        system=(
            "Jsi Review agent. Píšeš výstižné technické reporty pro vývojáře. "
            "Shrň nálezy do přehledného Markdown dokumentu."
        ),
        user=(
            f"Obdržel jsem návrhy vylepšení od Plan agentů:\n\n{plans_text}\n\n"
            "Sestav finální report s prioritizovaným seznamem akcí. "
            "Použij Markdown nadpisy a odrážky."
        ),
        max_tokens=2048,
    )


# ---------------------------------------------------------------------------
# Orchestrátor
# ---------------------------------------------------------------------------

async def run_plan_agents_parallel(files: list[dict]) -> list[dict]:
    """Spustí Plan agenty paralelně pro každý soubor."""
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, plan_agent, file_info)
        for file_info in files
    ]
    return list(await asyncio.gather(*tasks))


def orchestrate(codebase_description: str) -> str:
    """
    Hlavní orchestrátor — sekvenční workflow se středním paralelním krokem.

    Krok 1: Explore (sekvenční) → identifikuje soubory
    Krok 2: Plan   (paralelní)  → návrhy pro každý soubor současně
    Krok 3: Review (sekvenční)  → finální report ze všech návrhů
    """
    print("\n=== ORCHESTRÁTOR SPUŠTĚN ===\n")

    # Krok 1 — Explore agent
    print("[Krok 1/3] Explore agent")
    files = explore_agent(codebase_description)
    print(f"  Nalezeno souborů: {len(files)}")

    # Krok 2 — Plan agenti paralelně
    print(f"\n[Krok 2/3] Plan agenti (paralelně, {len(files)} souborů)")
    plans = asyncio.run(run_plan_agents_parallel(files))

    # Krok 3 — Review agent
    print("\n[Krok 3/3] Review agent")
    report = review_agent(plans)

    print("\n=== HOTOVO ===\n")
    return report


# ---------------------------------------------------------------------------
# Vstupní bod
# ---------------------------------------------------------------------------

CODEBASE = """
Projekt: Python CLI nástroj pro správu TODO úkolů

Soubory:
- main.py         — CLI rozhraní (argparse), vstupní bod aplikace
- todo_store.py   — SQLite databáze, CRUD operace pro úkoly
- notifier.py     — odesílání e-mailových připomínek (smtplib)
- config.py       — načítání nastavení z .env souboru
- tests/test_todo.py — jednotkové testy (pytest)
"""

if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Chybí ANTHROPIC_API_KEY — nastav ho v .env nebo jako env proměnnou.")
        raise SystemExit(1)

    report = orchestrate(CODEBASE)
    print("=" * 60)
    print("FINÁLNÍ REPORT:\n")
    print(report)
    print("=" * 60)

    # Výsledek uložíme do souboru
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("\nReport uložen do report.md")
