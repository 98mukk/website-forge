"""The Golden Gauntlet: 5 fixed briefs that benchmark the Forge over time.

python3 bench.py          -> shows usage, builds NOTHING (API cost)
python3 bench.py --dry    -> prints the briefs
python3 bench.py --run    -> runs all 5 against a live server, logs a row to benchmark.md
"""
import datetime
import subprocess
import sys
import time

import httpx

BASE = "http://127.0.0.1:8000"

BRIEFS = [
    ("Solstice Roasters, a small-batch coffee roastery in Traverse City, Michigan. "
     "Single-origin beans, tasting-room visits, wholesale for cafes.", "warm and editorial"),
    ("Kanna Labs, a biotech startup that sequences soil microbiomes so farms can cut "
     "fertilizer use. Serious science, hopeful tone.", "clean and minimal"),
    ("Ironline Strength, a powerlifting gym in Gary, Indiana. Calibrated plates, "
     "chalk everywhere, coaching for first meets.", "bold and industrial"),
    ("Aster and Vale, a boutique estate-law firm for family-owned businesses. "
     "Third-generation clients, succession planning, quiet confidence.", "classic and premium"),
    ("Nightglass, an indie studio making a neon-noir detective game set in a flooded "
     "city. Wishlist push before the demo drops.", "dark and cinematic"),
]

def git_hash():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "-"

def run_one(brief, style):
    """POST one brief, poll /status until done. Returns score, or None if capped."""
    r = httpx.post(f"{BASE}/build", data={"brief": brief, "style": style}, timeout=30)
    if r.status_code == 429:
        print("⚖️ Daily build cap reached, gauntlet halted")
        return None
    r.raise_for_status()
    for _ in range(360):                       # up to 30 minutes per build
        time.sleep(5)
        s = httpx.get(f"{BASE}/status", timeout=10).json()
        if s.get("error"):
            print(f"💥 Build failed: {s['error']}")
            return 0
        if s.get("done"):
            return s.get("score") or 0
    print("⏳ Timed out waiting on the Forge")
    return 0

def log_row(scores):
    avg = round(sum(scores) / len(scores), 1)
    today = datetime.date.today().isoformat()
    row = f"| {today} | {git_hash()} | " + " | ".join(str(s) for s in scores) + f" | {avg} |\n"
    try:
        existing = open("benchmark.md").read()
    except FileNotFoundError:
        existing = ""
    with open("benchmark.md", "a") as f:
        if "| date |" not in existing:
            f.write("# Forge Benchmark: the Golden Gauntlet\n\n")
            f.write("| date | commit | b1 | b2 | b3 | b4 | b5 | avg |\n")
            f.write("|---|---|---|---|---|---|---|---|\n")
        f.write(row)
    print(f"📄 Logged to benchmark.md: avg {avg}/10")

def run_gauntlet():
    scores = []
    for i, (brief, style) in enumerate(BRIEFS, 1):
        print(f"🏗️ Gauntlet {i}/5: {brief[:60]}...")
        score = run_one(brief, style)
        if score is None:
            break
        print(f"⚖️ Scored {score}/10")
        scores.append(score)
    if len(scores) == len(BRIEFS):
        log_row(scores)
    else:
        print(f"📦 Gauntlet incomplete ({len(scores)}/5), no row logged")

if __name__ == "__main__":
    if "--dry" in sys.argv:
        for i, (brief, style) in enumerate(BRIEFS, 1):
            print(f"{i}. {brief}  [style: {style}]")
    elif "--run" in sys.argv:
        run_gauntlet()
    else:
        print("🏗️ Golden Gauntlet. Builds cost API money, so nothing runs by default.")
        print("   python3 bench.py --dry   print the 5 briefs")
        print("   python3 bench.py --run   build all 5 against http://127.0.0.1:8000 and log to benchmark.md")
