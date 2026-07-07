import base64
import json
import os
import threading

import anthropic
from dotenv import load_dotenv
load_dotenv()

from fastapi import BackgroundTasks, FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from memory import recall, rules, ingest
from eval import judge
from art import paint
from brandkit import forge_kit
from pages import build_pages, package
import db
import guards

client = anthropic.Anthropic()
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# On a fresh server (like Render) the deck starts empty: seal it on boot.
if rules.count() == 0:
    ingest()

# The gate seal: when FORGE_KEY is set, /build and /revise demand it.
# Unset (local dev) = gate stays open.
FORGE_KEY = os.environ.get("FORGE_KEY", "")

def gate_open(key):
    return not FORGE_KEY or key == FORGE_KEY

# Feature flags
ART_DEPT = True      # flip to False to fall back to picsum placeholders
BRAND_KIT = True     # the $20k centerpiece: forge the kit, build FROM it
MULTI_PAGE = True    # the Package: 4 pages + zip delivery

# The Forge's live status board, polled by GET /status
STATUS = {"stage": "", "log": [], "done": False, "error": None,
          "score": None, "package": None, "kit": None}

# Last build, remembered for POST /revise
LAST = {"order": None, "home": None, "pages": None, "kit_html": ""}

# One forge, one fire: held while a pipeline runs, released in its finally block
BUSY = threading.Lock()

def reset_status():
    STATUS.update(stage="", log=[], done=False, error=None,
                  score=None, package=None, kit=None)

def stage(msg):
    print(msg)
    STATUS["stage"] = msg
    STATUS["log"].append(msg)

def sanitize(html):
    return html.replace(" — ", ", ").replace("—", "-")   # em-dash ban, enforced in code

SYSTEM = """You are an elite web designer with ruthless taste. You build single-file HTML sites that look human-crafted, never AI-generated.

Before designing, use the search_style_memory tool to look up our proven design rules for this kind of site. Apply what it returns.

HARD RULES (violating any = failure):
- ONE accent color, used sparingly. Neutral base (off-white or off-black, never pure #fff/#000 backgrounds with pure black text). NO purple/violet gradients ever.
- Real font pairing loaded from Google Fonts: a characterful display font for headlines + a clean sans for body. NEVER Inter, Roboto, Arial, or system fonts.
- Hero: headline max 2 lines, subtext max 20 words, CTA visible without scrolling. NOT centered-by-default: prefer split or asymmetric layouts.
- NO three-equal-cards feature rows. Each section uses a DIFFERENT layout family (split, bento, full-width, alternating, marquee). Never repeat a layout twice in a row.
- Real images: use https://picsum.photos/seed/{descriptive-word}/{width}/{height} with a different seed per image. Every site needs at least 3 images. No gray placeholder divs.
- Generous whitespace (large section padding), a clear type scale, subtle hover states and scroll animations (respect prefers-reduced-motion).
- Copy: concrete and specific, no filler verbs (Elevate, Seamless, Unleash, Revolutionize). Realistic names and organic numbers (47.2%, not 50%). No em-dashes anywhere.
- Small uppercase section labels (eyebrows): maximum 1 per 3 sections.
- Mobile: everything collapses to clean single column under 768px.
- SIGNATURE CLOSER: end the page with a text-over-glow CTA section built the proven way: one absolutely positioned atmospheric cover image at z-0, one top-down gradient scrim in the page background color (solid through ~20% height, transparent by 80%) so the headline sits clean while the glow blooms behind the bottom, then glass action cards: translucent white at 10-12% alpha, backdrop-blur 8px, rounded corners, the whole card is the link, hover brightens to ~20% alpha, no borders, no shadows.

Output ONLY the complete HTML document, no explanations."""

TOOLS = [{
    "name": "search_style_memory",
    "description": "Search Lake Shore Digital's design-rule memory for proven style guidance. Call this before designing to fetch rules that match the site you are about to build.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "What design intel to look up, e.g. 'minimal premium layout rules'"}
        },
        "required": ["query"],
    },
}]

def summon(brief, image_blocks=None):
    content = list(image_blocks or [])
    if image_blocks:
        brief += ("\n\nReference images are attached. Match their composition, spacing, "
                  "and overall mood. Take colors, fonts, and copy from the brief and the design memory.")
    content.append({"type": "text", "text": f"Build a complete single-file HTML website. Brief: {brief}"})
    messages = [{"role": "user", "content": content}]
    while True:
        r = client.messages.create(
            model="claude-opus-4-8", max_tokens=16000,
            system=SYSTEM, tools=TOOLS, messages=messages,
        )
        if r.stop_reason != "tool_use":
            break
        # Claude activated the search card: run it, hand back the results
        messages.append({"role": "assistant", "content": r.content})
        results = []
        for block in r.content:
            if block.type == "tool_use":
                print(f"🔍 Claude searched memory for: {block.input['query']}")
                intel = recall(block.input["query"])
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": intel})
        messages.append({"role": "user", "content": results})
    return "".join(b.text for b in r.content if b.type == "text")

POLISH_SYSTEM = """You are a senior front-end polish specialist. You receive a finished draft site and upgrade its LIVELINESS and CLEANLINESS without changing its content, copy, brand, or section order.

Apply the MOTION AND POLISH INTEL provided, plus this checklist:
- Scroll reveals: one fadeInUp keyframe (opacity 0 + translateY(40px) to 0, .6s ease-out) driven by IntersectionObserver at threshold 0.2, staggered ~100ms per sibling.
- Hover states on EVERY card, button, and link: 200ms color transitions, at most one subtle transform.
- Spacing discipline: one consistent max-width wrapper, one section padding rhythm, aligned edges everywhere.
- Detail polish: branded ::selection color, hairline borders tinted toward the accent, visible focus-visible rings.
- Ambient background motion stays SLOW (20s+); everything collapses under prefers-reduced-motion.
- Remove every em-dash. Fix any spacing or alignment sloppiness you see.

Output ONLY the complete upgraded HTML document, no explanations."""

def polish(brief, html):
    intel = recall("scroll reveal stagger hover states motion easing durations", k=4)
    intel += "\n\n" + recall("section spacing rhythm container width detail polish selection hairline borders", k=4)
    r = client.messages.create(
        model="claude-opus-4-8", max_tokens=16000,
        system=POLISH_SYSTEM,
        messages=[{"role": "user", "content":
            f"Brief: {brief}\n\nMOTION AND POLISH INTEL:\n{intel}\n\nDRAFT SITE:\n{html}"}],
    )
    return "".join(b.text for b in r.content if b.type == "text")

def run_build(brief, style, image_blocks):
    """The full pipeline, run as a BackgroundTask while /status is polled."""
    try:
        order = f"{brief}. Style direction: {style}"
        kit_html = ""

        if MULTI_PAGE:
            order += ("\n\nThe site has 4 pages. This is the HOME page: include a header nav "
                      "with links index.html (Home), about.html, services.html, contact.html.")

        if BRAND_KIT:
            stage("📜 Forging the brand kit")
            kit_html, tokens = forge_kit(order)
            with open("static/kit.html", "w") as f:
                f.write(kit_html)
            STATUS["kit"] = "/static/kit.html"
            if tokens:
                order += ("\n\nBUILD THE SITE FROM THIS BRAND KIT. Obey these tokens exactly "
                          "(colors with their ratios, fonts, radius, voice): "
                          + json.dumps(tokens))

        if ART_DEPT:
            try:
                stage("🍌 Art Department painting the imagery")
                assets = paint(order, n=3)
                order += ("\n\nUSE ONLY these locally generated images, they are already on the server: "
                          + ", ".join(assets)
                          + ". Reference them exactly by those paths. Do NOT use picsum or any external image URLs.")
            except Exception as e:
                stage(f"🍌 Art Department misfire ({e}); falling back to placeholders")

        if image_blocks:
            stage(f"🔴 Eyes engaged: {len(image_blocks)} reference image(s)")

        stage("🏗️ Summoning the home page")
        html = summon(order, image_blocks)
        stage("✨ Polish pass: upgrading motion and spacing")
        html = polish(order, html)
        html = sanitize(html)
        with open("site.html", "w") as f:
            f.write(html)

        site_pages = {"index": html}
        if MULTI_PAGE:
            stage("📄 Forging the sub-pages")
            site_pages = build_pages(order, html, summon)
            stage("📦 Sealing the package")
            zip_path = package(site_pages, kit_html)
            stage(f"📦 Package sealed: {zip_path}")
            STATUS["package"] = "/static/forge-package.zip"

        stage("⚖️ The Judge weighs the verdict")
        score, flaws = judge(html)
        stage(f"⚖️ Verdict: {score}/10")
        STATUS["score"] = score

        db.log_build(brief, style, score, "static/forge-package.zip")
        if score >= 8:
            try:
                import taste
                taste.save_winner(html, score, order)
                stage("🏆 Winner sealed into the taste vault")
            except Exception as e:
                print(f"🏆 Taste vault unavailable ({e})")

        LAST.update(order=order, home=html, pages=site_pages, kit_html=kit_html)
        stage("✅ Build complete")
    except Exception as e:
        print(f"💥 Build failed: {e}")
        STATUS["error"] = str(e)
        try:  # failed builds still spent credits: they count against the cap
            db.log_build(brief, style, None, "FAILED")
        except Exception as log_err:
            print(f"📕 Ledger write failed: {log_err}")
    finally:
        STATUS["done"] = True
        BUSY.release()

def run_revise(instruction):
    """One summon pass on the stored home page, then re-package + re-judge."""
    try:
        order = LAST["order"]
        stage("🔧 Revising the home page")
        prompt = (f"{order}\n\nHere is the CURRENT home page HTML:\n{LAST['home']}\n\n"
                  f"Revise it per this instruction, changing nothing else: {instruction}\n"
                  "Output ONLY the complete revised HTML document.")
        html = sanitize(summon(prompt))
        with open("site.html", "w") as f:
            f.write(html)

        site_pages = dict(LAST["pages"] or {})
        site_pages["index"] = html
        stage("📦 Re-sealing the package")
        zip_path = package(site_pages, LAST["kit_html"])
        stage(f"📦 Package sealed: {zip_path}")
        STATUS["package"] = "/static/forge-package.zip"
        if LAST["kit_html"]:
            STATUS["kit"] = "/static/kit.html"

        stage("⚖️ The Judge weighs the revision")
        score, flaws = judge(html)
        stage(f"⚖️ Verdict: {score}/10")
        STATUS["score"] = score

        LAST.update(home=html, pages=site_pages)
        db.log_build(f"REVISION: {instruction}", "revision", score, "static/forge-package.zip")
        stage("✅ Revision complete")
    except Exception as e:
        print(f"💥 Revision failed: {e}")
        STATUS["error"] = str(e)
        try:  # failed revisions count too
            db.log_build(f"REVISION: {instruction}", "revision", None, "FAILED")
        except Exception as log_err:
            print(f"📕 Ledger write failed: {log_err}")
    finally:
        STATUS["done"] = True
        BUSY.release()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.post("/build")
async def build(background_tasks: BackgroundTasks,
                brief: str = Form(...), style: str = Form("clean and minimal"),
                refs: list[UploadFile] = File(default=[]), key: str = Form("")):
    if not gate_open(key):
        return JSONResponse(status_code=401, content={"error": "the forge is sealed: missing or wrong key"})
    if not guards.allowed():
        return JSONResponse(status_code=429, content={"error": "daily build cap reached"})

    image_blocks = []
    for ref in refs[:3]:                                   # the Eyes: max 3 references
        data = await ref.read()
        if not data:
            continue
        image_blocks.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": ref.content_type or "image/png",
                "data": base64.standard_b64encode(data).decode(),
            },
        })

    if not BUSY.acquire(blocking=False):
        return JSONResponse(status_code=429, content={"error": "build in progress"})
    reset_status()
    stage("🔥 Build started")
    background_tasks.add_task(run_build, brief, style, image_blocks)
    return {"started": True}

@app.get("/status")
def status():
    return STATUS

@app.get("/site", response_class=HTMLResponse)
def site():
    try:
        with open("site.html") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("No site forged yet.", status_code=404)

@app.post("/revise")
def revise(background_tasks: BackgroundTasks, instruction: str = Form(...), key: str = Form("")):
    if not gate_open(key):
        return JSONResponse(status_code=401, content={"error": "the forge is sealed: missing or wrong key"})
    if not guards.allowed():
        return JSONResponse(status_code=429, content={"error": "daily build cap reached"})
    if not LAST["home"]:
        return JSONResponse(status_code=400, content={"error": "no build to revise yet"})
    if not BUSY.acquire(blocking=False):
        return JSONResponse(status_code=429, content={"error": "build in progress"})
    reset_status()
    stage("🔧 Revision started")
    background_tasks.add_task(run_revise, instruction)
    return {"started": True}
