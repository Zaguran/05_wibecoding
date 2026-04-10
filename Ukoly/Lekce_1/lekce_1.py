"""
Lekce 1 - Python skript pro LLM API s nástrojem (tool use)

Krok 1: llama3.1:8b zjistí prvních 30 prvočísel pomocí nástroje
Krok 2: výsledek odešle do qwen2.5-coder:14b k ověření
Krok 3: veškerá komunikace se loguje do lekce_1.log
"""

import json
import logging
import os

import ollama
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Konfigurace
# ---------------------------------------------------------------------------

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_1 = os.getenv("MODEL_1", "llama3.1:8b")
MODEL_2 = os.getenv("MODEL_2", "qwen2.5-coder:14b")
LOG_FILE = "lekce_1.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Nástroj: výpočet prvočísel
# ---------------------------------------------------------------------------

def get_first_n_primes(n: int) -> list[int]:
    """Vrátí prvních n prvočísel."""
    primes: list[int] = []
    candidate = 2
    while len(primes) < n:
        if all(candidate % p != 0 for p in primes):
            primes.append(candidate)
        candidate += 1
    return primes


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_first_n_primes",
            "description": "Vrátí prvních N prvočísel.",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Počet prvočísel, která mají být vrácena.",
                    }
                },
                "required": ["n"],
            },
        },
    }
]

# ---------------------------------------------------------------------------
# Hlavní logika
# ---------------------------------------------------------------------------

def main() -> None:
    client = ollama.Client(host=OLLAMA_URL)
    logger.info("Spuštěn skript lekce_1.py | OLLAMA_URL=%s", OLLAMA_URL)

    # --- Krok 1: llama3.1:8b + tool use → prvních 30 prvočísel -------------

    logger.info("=" * 60)
    logger.info("KROK 1 — Model: %s", MODEL_1)

    user_prompt = "Pomocí nástroje get_first_n_primes zjisti prvních 30 prvočísel."
    messages: list[dict] = [{"role": "user", "content": user_prompt}]

    logger.info("Odesláno uživatelem: %s", user_prompt)

    response = client.chat(model=MODEL_1, messages=messages, tools=TOOLS)
    logger.info("Odpověď modelu (raw): %s", response.model_dump_json())

    primes: list[int] = []

    if response.message.tool_calls:
        for call in response.message.tool_calls:
            fn_name = call.function.name
            fn_args = call.function.arguments or {}
            n = int(fn_args.get("n", 30))
            logger.info("Model volá nástroj: %s(n=%s)", fn_name, n)

            if fn_name == "get_first_n_primes":
                primes = get_first_n_primes(n)
                logger.info("Výsledek nástroje: %s", primes)

        # Odešleme výsledek nástroje zpět modelu
        messages.append(response.message.model_dump())
        messages.append(
            {
                "role": "tool",
                "content": json.dumps(primes),
            }
        )

        final_1 = client.chat(model=MODEL_1, messages=messages)
        logger.info("Finální odpověď %s: %s", MODEL_1, final_1.message.content)
    else:
        # Model nepoužil nástroj — spočítáme sami a logujeme
        logger.warning("Model nepoužil nástroj, počítáme prvočísla lokálně.")
        primes = get_first_n_primes(30)
        logger.info("Prvočísla (lokální výpočet): %s", primes)

    # --- Krok 2: qwen2.5-coder:14b ověří, zda jsou čísla prvočísla ---------

    logger.info("=" * 60)
    logger.info("KROK 2 — Model: %s", MODEL_2)

    verification_prompt = (
        f"Jsou tato čísla prvočísla? Ověř každé z nich a odpověz stručně: {primes}"
    )
    messages_2: list[dict] = [{"role": "user", "content": verification_prompt}]

    logger.info("Odesláno uživatelem: %s", verification_prompt)

    response_2 = client.chat(model=MODEL_2, messages=messages_2)
    answer = response_2.message.content
    logger.info("Odpověď %s: %s", MODEL_2, answer)

    # --- Výsledek na stdout -------------------------------------------------

    logger.info("=" * 60)
    logger.info("HOTOVO — log uložen do %s", LOG_FILE)

    print("\n" + "=" * 60)
    print(f"Prvočísla (prvních 30): {primes}")
    print(f"\nOvěření od {MODEL_2}:")
    print(answer)
    print("=" * 60)


if __name__ == "__main__":
    main()
