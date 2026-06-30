import anthropic, base64
client = anthropic.Anthropic()

with open("ref.png", "rb") as f:
    img = base64.standard_b64encode(f.read()).decode()

r = client.messages.create(
    model="claude-opus-4-8", max_tokens=16000,
    system="You are an elite web designer. Copy the reference image's visual style exactly — its colors, fonts, spacing, and layout feel. No generic AI-slop.",
    messages=[{"role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img}},
        {"type": "text", "text": "Build a complete single-file HTML website in this exact visual style. It's a portfolio for Maximo Alanis, a paid-media marketer."},
    ]}],
)
with open("site.html", "w") as f:
    f.write(r.content[0].text)
print("Done — site.html copied from the image!")