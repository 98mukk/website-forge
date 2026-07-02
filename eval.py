import sys
import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic()

def judge(html):
    r = client.messages.create(
        model="claude-opus-4-8", max_tokens=600,
        system="""You are a ruthless design judge for Lake Shore Digital.
Score the website 1-10 against these laws:
- ONE accent color, rationed (not wallpaper). No purple gradients.
- Real font pairing from Google Fonts (never Inter/Roboto/Arial/system).
- Real images present (not gray placeholder divs).
- Varied section layouts (no repeated layout families, no three-equal-cards).
- Generous whitespace, clear type scale, hover states.
- Concrete copy, no filler verbs, no em-dashes.
Reply in EXACTLY this format:
SCORE: <n>/10
- <reason>
- <reason>
- <reason>""",
        messages=[{"role": "user", "content": html[:60000]}],
    )
    return r.content[0].text

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "site.html"
    print(f"Judging {path}...")
    print(judge(open(path).read()))
