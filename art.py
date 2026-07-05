"""The Art Department: MiniMax paints real brand assets so placeholder images die."""
import json
import re
import subprocess
from pathlib import Path

import anthropic
from dotenv import load_dotenv
load_dotenv()

from memory import recall

client = anthropic.Anthropic()
STATIC = Path("static")
STATIC.mkdir(exist_ok=True)

def plan_shots(brief, n=3):
    """Claude the art director: brief + deck intel -> MiniMax image specs."""
    intel = recall("imagery art direction abstract hero atmosphere brand gradients", k=4)
    r = client.messages.create(
        model="claude-opus-4-8", max_tokens=1000,
        system="You are a ruthless art director. Reply ONLY with a JSON array, no prose.",
        messages=[{"role": "user", "content": f"""Brief: {brief}

ART DIRECTION INTEL:
{intel}

Design {n} website images: one wide hero background first, then supporting section images.
Rules: abstract and atmospheric, brand-colored, premium; no text inside images, no faces, no logos, no busy collages.
Reply ONLY with a JSON array like:
[{{"file": "hero", "prompt": "detailed image prompt", "width": 1920, "height": 1080}}]"""}],
    )
    match = re.search(r"\[.*\]", r.content[0].text, re.S)
    return json.loads(match.group(0))

def paint(brief, n=3):
    """Generate n images into static/. Returns their /static/... URL paths."""
    shots = plan_shots(brief, n)
    paths = []
    for shot in shots[:n]:
        out = STATIC / f"{shot['file']}.png"
        w = max(512, min(2048, int(shot.get("width", 1536)) // 8 * 8))
        h = max(512, min(2048, int(shot.get("height", 1024)) // 8 * 8))
        print(f"🍌 Painting {out.name}: {shot['prompt'][:70]}...")
        subprocess.run(
            ["mmx", "image", "generate", "--prompt", shot["prompt"],
             "--width", str(w), "--height", str(h), "--out", str(out)],
            check=True, capture_output=True, text=True,
        )
        paths.append(f"/static/{out.name}")
    return paths

if __name__ == "__main__":
    print(paint("Dark premium AI agency landing page. Purple and green light on near-black."))
