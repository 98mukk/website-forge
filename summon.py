import anthropic
client = anthropic.Anthropic()

def plan(idea):
    r = client.messages.create(
        model="claude-opus-4-8", max_tokens=2000,
        system="You are an elite brand designer. Output a tight design brief: ONE accent color (hex), a font pairing, the vibe, and 4 page sections. Specific and concise.",
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

idea = input("What site should I summon? ")
styles = ["bold and dark", "clean and minimal", "warm and editorial"]

sites = []                                  # the roster of fighters
for i, style in enumerate(styles, 1):
    print(f"Clone {i} building ({style})...")
    sites.append(summon(plan(f"{idea}. Style: {style}")))

print("Proctor judging...")
verdict = client.messages.create(
    model="claude-opus-4-8", max_tokens=500,
    system="You are a ruthless design judge. You'll get 3 websites. Reply with ONLY the number (1, 2, or 3) of the best one.",
    messages=[{"role": "user", "content": f"SITE 1:\n{sites[0]}\n\nSITE 2:\n{sites[1]}\n\nSITE 3:\n{sites[2]}"}],
).content[0].text

winner = int(verdict.strip()[0])            # grab the number
with open("winner.html", "w") as f:
    f.write(sites[winner - 1])
print(f"Proctor crowned Site {winner}! Saved as winner.html 🏆")
