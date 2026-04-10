# Lekce 1 — Python skript pro LLM API s nástrojem (Tool Use)

## Zadání

Napsat Python skript, který:

1. **Krok 1** — Připojí se k Ollama, modelu `llama3.1:8b`, a pomocí nástroje (`tool use`) zjistí prvních 30 prvočísel.
2. **Krok 2** — Výsledek odešle modelu `qwen2.5-coder:14b` a zeptá se, zda uvedená čísla jsou skutečně prvočísla.
3. **Krok 3** — Veškerou komunikaci (co bylo odesláno a co přišlo) monitoruje do logu, aby bylo ověřitelné, že kód funguje správně.

---

## Struktura

```
Ukoly/Lekce_1/
├── lekce_1.py      # hlavní skript (vše v jednom souboru)
├── .env            # konfigurace prostředí (OLLAMA_URL)
├── lekce_1.log     # log komunikace (vytvoří se při spuštění)
├── zadani.txt      # původní zadání úkolu
└── README.md       # tento soubor
```

---

## Verze

| Položka    | Hodnota            |
|------------|--------------------|
| Verze      | 1.0.0              |
| Python     | 3.10+              |
| Model 1    | llama3.1:8b        |
| Model 2    | qwen2.5-coder:14b  |
| Ollama     | lokální instalace  |

---

## Požadavky

Nainstaluj závislosti:

```bash
pip install ollama python-dotenv
```

Ujisti se, že máš v Ollama stažené potřebné modely:

```bash
ollama pull llama3.1:8b
ollama pull qwen2.5-coder:14b
```

---

## Konfigurace

Skript načítá nastavení ze souboru `.env` ve stejné složce:

```env
OLLAMA_URL=http://localhost:11434
```

---

## Spuštění

```bash
cd Ukoly/Lekce_1
python lekce_1.py
```

---

## Log

Po spuštění se ve složce `Ukoly/Lekce_1/` vytvoří soubor **[lekce_1.log](lekce_1.log)** s kompletním záznamem komunikace:

- co bylo odesláno každému modelu
- jaké nástroje model zavolal a s jakými argumenty
- výsledek nástroje vrácený zpět modelu
- finální odpovědi obou modelů

Příklad výstupu v logu:

```
2026-04-10 12:00:00 [INFO] Spuštěn skript lekce_1.py | OLLAMA_URL=http://localhost:11434
2026-04-10 12:00:00 [INFO] ============================================================
2026-04-10 12:00:00 [INFO] KROK 1 — Model: llama3.1:8b
2026-04-10 12:00:00 [INFO] Odesláno uživatelem: Pomocí nástroje get_first_n_primes zjisti prvních 30 prvočísel.
2026-04-10 12:00:05 [INFO] Model volá nástroj: get_first_n_primes(n=30)
2026-04-10 12:00:05 [INFO] Výsledek nástroje: [2, 3, 5, 7, 11, ...]
2026-04-10 12:00:07 [INFO] Finální odpověď llama3.1:8b: Prvních 30 prvočísel je: ...
2026-04-10 12:00:07 [INFO] ============================================================
2026-04-10 12:00:07 [INFO] KROK 2 — Model: qwen2.5-coder:14b
2026-04-10 12:00:07 [INFO] Odesláno uživatelem: Jsou tato čísla prvočísla? ...
2026-04-10 12:00:15 [INFO] Odpověď qwen2.5-coder:14b: Ano, všechna uvedená čísla jsou prvočísla ...
```
