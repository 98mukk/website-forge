"""The Brand Kit Generator: brief -> a real brand-kit artifact the site is built FROM."""
import json
import re

import anthropic
from dotenv import load_dotenv
load_dotenv()

from memory import recall

client = anthropic.Anthropic()

KIT_SYSTEM = """You are an elite brand strategist for Lake Shore Digital. From a client brief you forge a COMPLETE brand kit as a single-file HTML page: the polished artifact a client pays five figures for.

The kit must follow the six-part anatomy:
1. Brand essence and messaging: positioning line, 3 message pillars, voice rules with banned words.
2. Logo laws: recommended construction, a clearspace rule tied to a wordmark element, minimum sizes, 4-6 don'ts.
3. Color system: exact hexes with named roles and usage ratios (like 60/30/9/1), light and dark surface guidance, accessibility notes.
4. Type system: a real Google Fonts pairing (never Inter/Roboto/Arial), full scale with sizes, weights, and tracking.
5. Imagery art direction: mood, subjects, treatments, and bans.
6. Usage rules: dos and don'ts for applying the system.

The page itself must be beautiful and obey the anti-slop laws: one accent color, real font pairing loaded from Google Fonts, no purple gradients, no em-dashes anywhere, generous whitespace, color swatches rendered as real colored blocks with hex labels, varied section layouts.

CRITICAL: embed a machine-readable token block exactly like this (real values, valid JSON):
<script id="brand-tokens" type="application/json">{"brand":"Name","positioning":"one line","colors":{"base":{"hex":"#...","ratio":"60%"},"surface":{"hex":"#...","ratio":"30%"},"accent":{"hex":"#...","ratio":"9%"},"signal":{"hex":"#...","ratio":"1%"}},"fonts":{"display":"Font Name","body":"Font Name"},"radius":"8px","voice":["rule 1","rule 2","banned: word, word"],"imagery":"one-line art direction"}</script>

Output ONLY the complete HTML document, no explanations."""

def forge_kit(brief):
    """Returns (kit_html, tokens_dict). The site is then built FROM these tokens."""
    intel = recall("brand kit anatomy color ratios type system logo clearspace laws", k=4)
    intel += "\n\n" + recall("brand voice copy register banned words concrete", k=3)
    r = client.messages.create(
        model="claude-opus-4-8", max_tokens=16000, system=KIT_SYSTEM,
        messages=[{"role": "user", "content":
            f"Forge a complete brand kit. Client brief: {brief}\n\nPROVEN BRAND-SYSTEM INTEL:\n{intel}"}],
    )
    html = "".join(b.text for b in r.content if b.type == "text")
    m = re.search(r'<script id="brand-tokens"[^>]*>(.*?)</script>', html, re.S)
    tokens = {}
    if m:
        try:
            tokens = json.loads(m.group(1))
        except json.JSONDecodeError:
            print("📜 Token block unreadable; building from the kit page text instead")
    return html, tokens

if __name__ == "__main__":
    html, tokens = forge_kit("Lake Shore Digital, an AI agency. Dark, premium, fintech energy.")
    with open("static/kit.html", "w") as f:
        f.write(html)
    print(json.dumps(tokens, indent=2))
