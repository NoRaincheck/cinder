import re
from pathlib import Path

TWEE = Path("src/glass.twee").read_text()
PASSAGES = dict(re.findall(r"^::\s+(\S+)[^\n]*\n((?:(?!^::).)*)", TWEE, flags=re.M | re.S))
# Navigation renders as a bare `>` (no ending/return info); every other
# label is a story choice.
def story_links(body):
    out = []
    for m in re.finditer(r"\[\[([^\]|]+)\|([^\]]+)\]\]", body):
        if m.group(1).strip() != ">":
            out.append(m.group(0))
    return out

def test_max_three_story_choices():
    bad = {n: len(story_links(b)) for n, b in PASSAGES.items()
           if (n.startswith("S") or n == "Prologue-Intro") and len(story_links(b)) > 3}
    assert bad == {}, f"passages with >3 story choices: {sorted(bad.items())[:5]}"
