from pathlib import Path

STORIES = [
    {
        "file": "glass.html",
        "title": "Glass",
        "headline": "A fractured fairy tale",
        "description": "A conversation-oriented fairy tale in one room: steer the drawing-room talk as the Prince's parrot.",
    },
    {
        "file": "bronze.html",
        "title": "Bronze",
        "headline": "A fractured fairy tale",
        "description": "A puzzle-oriented Beauty and the Beast: return to the castle in the forest and find what holds you there.",
    },
]

TEMPLATE = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Cinder</title></head>
<body>
<main>
<h1>Cinder</h1>
{cards}
<footer><p>Glass and Bronze by Emily Short (2006), choice adaptations. Dialogue kept verbatim except parser artifacts.</p></footer>
</main>
</body>
</html>
"""

CARD = """<section><h2>{title}</h2><p><em>{headline}</em></p><p>{description}</p><p><a href="{file}">Play {title}</a></p></section>"""


def main():
    dist = Path("dist")
    for story in STORIES:
        target = dist / story["file"]
        if not target.exists():
            raise SystemExit(f"missing story artifact: {target}")
    cards = "\n".join(CARD.format(**s) for s in STORIES)
    (dist / "index.html").write_text(TEMPLATE.format(cards=cards))


if __name__ == "__main__":
    main()
