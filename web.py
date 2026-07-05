import base64

import anthropic
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from memory import recall, rules, ingest
from eval import judge
from art import paint

client = anthropic.Anthropic()
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# On a fresh server (like Render) the deck starts empty: seal it on boot.
if rules.count() == 0:
    ingest()

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

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.post("/build", response_class=HTMLResponse)
async def build(brief: str = Form(...), style: str = Form("clean and minimal"),
                refs: list[UploadFile] = File(default=[])):
    JUDGE_GATE = False   # flip to True to re-arm the Proctor
    ART_DEPT = True      # flip to False to fall back to picsum placeholders
    order = f"{brief}. Style direction: {style}"

    if ART_DEPT:
        try:
            assets = paint(order, n=3)
            order += ("\n\nUSE ONLY these locally generated images, they are already on the server: "
                      + ", ".join(assets)
                      + ". Reference them exactly by those paths. Do NOT use picsum or any external image URLs.")
        except Exception as e:
            print(f"🍌 Art Department misfire ({e}); falling back to placeholders")

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
    if image_blocks:
        print(f"🔴 Eyes engaged: {len(image_blocks)} reference image(s)")

    html = summon(order, image_blocks)
    print("✨ Polish pass: upgrading motion and spacing")
    html = polish(order, html)
    score = None

    if JUDGE_GATE:
        score, flaws = judge(html)
        print(f"⚖️ Gate 1 verdict: {score}/10")
        gates = 0
        while score < 7 and gates < 2:                 # the Judge Gate
            gates += 1
            print(f"🔥 Opening gate {gates}: rebuilding with fixes")
            html = summon(f"{order}\n\nA design judge scored the last attempt {score}/10. FIX THESE FLAWS:\n{flaws}", image_blocks)
            score, flaws = judge(html)
            print(f"⚖️ Gate {gates + 1} verdict: {score}/10")

    with open("site.html", "w") as f:
        f.write(html)
    headers = {"X-Judge-Score": str(score)} if score is not None else {}
    return HTMLResponse(content=html, headers=headers)
