# Agentic Engineering — Orchestrace AI agentů

Lekce 5, Úkol AgenticEngineering 1

Projekt demonstruje dvě orchestrační strategie s Anthropic SDK:
1. **Sekvenční + paralelní workflow** (`subagent_demo.py`)
2. **Dynamická smyčka s tool use** (`agentic_loop.py`)

Jako podkladový projekt slouží funkční TODO CLI aplikace (`main.py`, `todo_store.py`, `notifier.py`).

---

## Workflow 1 — Sekvenční + paralelní (`subagent_demo.py`)

```
[Explore agent]  →  [Plan agent ×N paralelně]  →  [Review agent]
   (sekvenční)           (paralelní)                 (sekvenční)
```

### Jak to funguje

**Krok 1 — Explore agent** dostane popis projektu a identifikuje klíčové soubory. Vrátí JSON seznam `[{file, purpose}, ...]`.

**Krok 2 — Plan agenti** běží paralelně (`asyncio.gather`). Každý dostane jeden soubor a navrhne 3 konkrétní vylepšení. Paralelní spuštění zkracuje celkový čas N× oproti sekvenčnímu.

**Krok 3 — Review agent** agreguje výstupy všech Plan agentů do finálního Markdown reportu s prioritizovaným seznamem akcí.

Výsledek se uloží do `report.md`.

---

## Workflow 2 — Dynamická smyčka (`agentic_loop.py`)

```
        ┌─────────────────────────────────────┐
        │                                     │
  fronta úkolů  →  agent rozhodne  →  decompose → přidá podúkoly do fronty
                        │
                        └──────────→  execute  → označí úkol jako hotový
                                          │
                                     (opakuj dokud fronta není prázdná)
```

### Jak to funguje

Agent dostane jediný vysokoúrovňový úkol (např. *"Vytvořit webovou aplikaci"*). V každé iteraci smyčky vybere první úkol z fronty a musí použít jeden ze dvou nástrojů:

| Nástroj | Kdy | Co se stane |
|---------|-----|-------------|
| `decompose_task` | Úkol je příliš velký nebo vágní | Rozloží ho na 2–4 podúkoly, ty se přidají na konec fronty |
| `execute_task` | Úkol je dost konkrétní | Popíše co bylo provedeno, úkol se označí jako hotový |

Agent tak rekurzivně rozkládá složité úkoly až na atomické kroky, které pak provede.

### Pojistky

- **`MAX_DEPTH = 3`** — na hloubce 3 agent nemůže dál rozkládat, musí použít `execute_task`
- **`MAX_ITERATIONS = 20`** — celková pojistka smyčky proti nekonečnému běhu
- **`tool_choice: any`** — agent musí vždy použít nástroj, nemůže odpovědět volným textem

### Ukázkový průběh

```
[01] ▶ Vytvořit webovou aplikaci pro správu projektů
       → rozloženo: Navrhnout DB schéma / Implementovat API / Vytvořit frontend

[02]   ▶ Navrhnout DB schéma
         → rozloženo: Definovat tabulky / Navrhnout indexy

[03]     ▶ Definovat tabulky pro projekty a úkoly
           ✓ Vytvořeny tabulky projects, tasks, users s FK vazbami

[04]     ▶ Navrhnout indexy a vztahy
           ✓ Přidány indexy na cizí klíče, definovány CASCADE pravidla
...
```

Stav fronty je průběžně ukládán do SQLite (`todo.db`) přes `todo_store.py`. Výsledný report se zapíše do `loop_report.md`.

---

## Konfigurace Claude Code agenta

Soubor `.claude/settings.json` konfiguruje chování Claude Code v tomto projektu:

- **MCP servery** — Google Drive, Gmail, Google Calendar (HTTP), fetch pro stahování dokumentace, filesystem pro přístup k souborům
- **Permissions** — povolené příkazy (`git`, `python3`, `find`, `grep`, …), zakázané destruktivní operace (`rm -rf`, `git push --force`)
- **Hooks** — `PostToolUse(Bash)` loguje každé spuštění příkazu, `Stop` zaznamená ukončení session

## Struktura projektu

```
Ukol_AgenticEngeniering_1/
├── .claude/
│   └── settings.json    # MCP servery, permissions, hooky pro Claude Code
├── agentic_loop.py      # Loop pattern — dynamická fronta s tool use
├── subagent_demo.py     # Sekvenční + paralelní workflow
├── main.py              # TODO CLI (argparse): add / list / done / delete / notify
├── todo_store.py        # SQLite CRUD operace
├── notifier.py          # E-mailové připomínky (smtplib)
├── config.py            # Konfigurace z .env
├── tests/
│   └── test_todo.py     # Pytest testy (7 testů)
├── .env.example         # Šablona proměnných prostředí
└── .gitignore
```

## Spuštění

```bash
# 1. Nastavení
cp .env.example .env
# Doplň ANTHROPIC_API_KEY do .env

# 2. Instalace závislostí
python3 -m venv .venv
source .venv/bin/activate
pip install anthropic python-dotenv pytest

# 3. Spuštění demo
python agentic_loop.py       # dynamická smyčka
python subagent_demo.py      # sekvenční + paralelní workflow

# 4. TODO CLI
python main.py add "Napsat testy" --due 2026-05-10
python main.py list
python main.py done 1

# 5. Testy
pytest tests/ -v
```

## Závislosti

| Balíček | Použití |
|---------|---------|
| `anthropic` | Anthropic SDK — volání Claude API, tool use |
| `python-dotenv` | Načítání `.env` konfigurace |
| `pytest` | Jednotkové testy |
