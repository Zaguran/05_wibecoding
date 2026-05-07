# Claude Code — Konfigurace agenta (Lekce 5, Úkol 2)

## MCP Servery

MCP (Model Context Protocol) servery rozšiřují schopnosti agenta o přístup k externím systémům.

| Server | Typ | Použití |
|--------|-----|---------|
| `google-drive` | HTTP | Čtení podkladů a ukládání výsledků na Google Drive |
| `gmail` | HTTP | Odesílání e-mailových reportů po dokončení analýzy |
| `google-calendar` | HTTP | Plánování opakovaných úkolů (code review, reporty) |
| `fetch` | stdio (`uvx mcp-server-fetch`) | Stahování webové dokumentace, README souborů, PyPI stránek |
| `filesystem` | stdio (`npx @modelcontextprotocol/server-filesystem`) | Přímý přístup k souborům projektu mimo kontext konverzace |

Konfigurace je v `.claude/settings.json`.

## Skilly (Skills)

Skilly jsou předdefinované specializované chování agenta, aktivované lomítkovými příkazy:

| Skill | Spuštění | Co dělá |
|-------|----------|---------|
| `claude-api` | `/claude-api` | Budování a ladění aplikací s Anthropic SDK, prompt caching |
| `simplify` | `/simplify` | Review změněného kódu — hledá duplicity, zjednodušuje |
| `review` | `/review` | Code review pull requestu |
| `security-review` | `/security-review` | Bezpečnostní audit změn na větvi |
| `init` | `/init` | Inicializace CLAUDE.md s dokumentací projektu |
| `fewer-permission-prompts` | `/fewer-permission-prompts` | Přidá allowlist do settings.json pro časté operace |
| `update-config` | `/update-config` | Úprava settings.json (hooky, permissions, env proměnné) |

## Subagenti

Subagenti jsou specializované instance agenta spouštěné přes `Agent` tool. Každý typ má svou sadu nástrojů a zaměření:

| Typ | Kdy použít |
|-----|------------|
| `Explore` | Rychlé hledání v kódu — soubory, symboly, patterns |
| `Plan` | Návrh implementace — architektura, trade-offs, kroky |
| `general-purpose` | Komplexní vícekrokové úkoly, výzkum |
| `claude-code-guide` | Otázky o Claude Code CLI, API, SDK |
| `statusline-setup` | Konfigurace status line |

Praktická ukázka orchestrace subagentů je v `subagent_demo.py`.

## Hooky

Hooky jsou shell příkazy spouštěné automaticky na určité události:

```
PostToolUse(Bash) → loguje každé spuštění bash příkazu do /tmp/claude_activity.log
Stop              → loguje ukončení session
```

## Permissions

```json
allow: git, python3, pip, uv, find, grep, cat, ls, mkdir, Read, Edit, Write
deny:  rm -rf, git push --force
```
