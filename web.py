import anthropic
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from memory import recall

client = anthropic.Anthropic()
app = FastAPI()
templates = Jinja2Templates(directory="templates")

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

def summon(brief):
    messages = [{"role": "user", "content": f"Build a complete single-file HTML website. Brief: {brief}"}]
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

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.post("/build", response_class=HTMLResponse)
def build(brief: str = Form(...), style: str = Form("clean and minimal")):
    html = summon(f"{brief}. Style direction: {style}")
    with open("site.html", "w") as f:
        f.write(html)
    return html
