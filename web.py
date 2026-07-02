import anthropic
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse


from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic()
app = FastAPI()

def summon(brief):
    r = client.messages.create(
        model="claude-opus-4-8", max_tokens=16000,
        system="You are a world-class web designer. ONE accent color used sparingly, a real font pairing from Google Fonts, generous whitespace, subtle animations. No generic AI-slop.",
        messages=[{"role": "user", "content": f"Build a complete single-file HTML website. Brief: {brief}"}],
    )
    return r.content[0].text

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h1>Website Forge</h1>
    <form method="post" action="/build">
      <input name="brief" placeholder="Describe the site" style="width:320px;padding:8px">
      <button>Summon</button>
    </form>
    """

@app.post("/build", response_class=HTMLResponse)
def build(brief: str = Form(...)):
    return summon(brief)
