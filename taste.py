"""The Taste Vault: distill a winning build into knowledge cards and re-seal the deck."""
import os

import anthropic
from dotenv import load_dotenv
load_dotenv()

import memory

client = anthropic.Anthropic()

TASTE_SYSTEM = """You are the taste archivist for Lake Shore Digital. You study a winning website build and distill WHY it worked into dense knowledge cards that future builds will recall.

Write 3 to 5 paragraphs. Each paragraph MUST start exactly with "FORGE WINNER, <TOPIC>:" where <TOPIC> is a short uppercase label like PALETTE, LAYOUT, MOTION, TYPE, or COPY. Each paragraph is one dense knowledge card: concrete rules with exact values (hexes and their ratios, font names, spacing rhythm, animation durations) plus the reasoning that made the choice work. Separate paragraphs with one blank line. No em-dashes. Output ONLY the paragraphs, nothing else."""

def save_winner(html, score, order):
    """Seal a scoring build (8+) into knowledge/winners.md, then re-ingest the deck."""
    r = client.messages.create(
        model="claude-opus-4-8", max_tokens=2000, system=TASTE_SYSTEM,
        messages=[{"role": "user", "content":
            f"This build scored {score}/10. The client order was:\n{order}\n\nTHE WINNING SITE:\n{html[:60000]}"}],
    )
    cards = "".join(b.text for b in r.content if b.type == "text").strip()
    path = "knowledge/winners.md"
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("# Forge Winners: what the scoring builds did right\n")
    with open(path, "a") as f:
        f.write(f"\n\n{cards}\n")
    memory.ingest()
    print("🏆 Winner sealed into the deck")

if __name__ == "__main__":
    save_winner(open("site.html").read(), 9, "test order: dark premium AI agency site")
