"""The Art Department: MiniMax paints real brand assets so placeholder images die."""
import json
import os
import re
import shutil
import subprocess
import time
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
    if shutil.which("mmx") is None:
        raise RuntimeError("mmx CLI not installed")
    shots = plan_shots(brief, n)
    fresh = []                         # (temp file, final file) painted this run
    for shot in shots[:n]:
        out = STATIC / f"new-{shot['file']}.png"
        w = max(512, min(2048, int(shot.get("width", 1536)) // 8 * 8))
        h = max(512, min(2048, int(shot.get("height", 1024)) // 8 * 8))
        print(f"🍌 Painting {out.name}: {shot['prompt'][:70]}...")
        cmd = ["mmx", "image", "generate", "--prompt", shot["prompt"],
               "--width", str(w), "--height", str(h), "--out", str(out)]
        key = os.environ.get("MINIMAX_API_KEY")
        if key:
            cmd += ["--api-key", key]
        for attempt in (1, 2):                 # transient rate limits: one retry per shot
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                fresh.append((out, STATIC / f"{shot['file']}.png"))
                break
            except subprocess.CalledProcessError as e:
                print(f"🍌 {out.name} attempt {attempt} failed: {(e.stderr or e.stdout or '').strip()[:200]}")
                if attempt == 2:
                    print(f"🍌 Skipping {out.name}")
                else:
                    time.sleep(5)
    if not fresh:
        raise RuntimeError("every mmx paint failed")
    temps = {temp for temp, final in fresh}
    for old in STATIC.glob("*.png"):   # clean the easel ONLY after fresh art exists
        if old not in temps:
            old.unlink()
    paths = []
    for temp, final in fresh:
        temp.rename(final)
        paths.append(f"/static/{final.name}")
    return paths

if __name__ == "__main__":
    print(paint("Dark premium AI agency landing page. Purple and green light on near-black."))
