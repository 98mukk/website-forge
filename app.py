import anthropic, base64
client = anthropic.Anthropic()

def plan(idea):
    r = client.messages.create(
        model="claude-opus-4-8", max_tokens=2000,
        system="You are a world-class web designer. Rules: ONE accent color used sparingly. A real font pairing (e.g. a characterful display font + clean sans body), loaded from Google Fonts. Generous whitespace and a clear type scale. Subtle hover states and scroll animations. Real-feeling copy, not lorem ipsum. NO generic AI-slop: no Inter-everywhere, no purple gradients, no cookie-cutter cards. Make it feel intentional and premium.",
        messages=[{"role": "user", "content": idea}],
    )
    return r.content[0].text

def summon(brief):
    r = client.messages.create(
        model="claude-opus-4-8", max_tokens=16000,
        system="You are an elite web designer. Follow the design brief exactly. Lots of whitespace, no generic AI-slop.",
        messages=[{"role": "user", "content": f"Build a complete single-file HTML website. Brief: {brief}"}],
    )
    return r.content[0].text

def sharingan(image_path, idea):
    with open(image_path, "rb") as f:
        img = base64.standard_b64encode(f.read()).decode()
    r = client.messages.create(
        model="claude-opus-4-8", max_tokens=16000,
        system="You are an elite web designer. Copy the reference image's visual style exactly. No generic AI-slop.",
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img}},
            {"type": "text", "text": f"Build a complete single-file HTML website in this exact style. For: {idea}"},
        ]}],
    )
    return r.content[0].text

def tournament(idea):
    styles = ["bold and dark", "clean and minimal", "warm and editorial"]
    sites = []
    for i, style in enumerate(styles, 1):
        print(f"Clone {i} building ({style})...")
        sites.append(summon(plan(f"{idea}. Style: {style}")))
    print("Judge deciding...")
    verdict = client.messages.create(
        model="claude-opus-4-8", max_tokens=500,
        system="You are a ruthless design judge. Given 3 sites, reply with ONLY the number (1, 2, or 3) of the best.",
        messages=[{"role": "user", "content": f"SITE 1:\n{sites[0]}\n\nSITE 2:\n{sites[1]}\n\nSITE 3:\n{sites[2]}"}],
    ).content[0].text
    winner = int(verdict.strip()[0])
    print(f"Judge crowned Site {winner} 🏆")
    return sites[winner - 1]

print("=== WEBSITE FORGE ===")
print("1 = Text summon")
print("2 = Image copy (needs ref.png in this folder)")
print("3 = Tournament (3 clones + judge)")
choice = input("Pick a jutsu (1/2/3): ")
idea = input("Describe the site: ")

if choice == "1":
    html = summon(plan(idea))
elif choice == "2":
    html = sharingan("ref.png", idea)
elif choice == "3":
    html = tournament(idea)
else:
    html = None
    print("Unknown jutsu.")

if html:
    with open("site.html", "w") as f:
        f.write(html)
    print("Done — site.html created!")