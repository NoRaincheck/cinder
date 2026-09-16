# tests/test_reachability.py
import re
from pathlib import Path

TWEE = Path("src/glass/glass.twee").read_text()
PASSAGES = dict(re.findall(r"^::\s+(\S+)[^\n]*\n((?:(?!^::).)*)", TWEE, flags=re.M | re.S))
LINKS = {n: re.findall(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", b) for n, b in PASSAGES.items()}
# Curated 3-choice spine (2026-09-15): scenes are named by their leading word,
# not by S<n>-Hub passages.
SCENES = ["Prologue", "Wondering", "Fitting", "Check-", "Theodora", "Lucinda", "End"]
# End-Cinderella-Executed is reachable via Cinderella-Tries → [[> |End-Cinderella-Executed]].
# No orphans in the curated spine; every non-meta passage must be reachable from Start.
# vars is a Chapbook meta-section, not a real passage.
ORPHANS = {"vars"}


def walk(start):
    seen, stack = set(), [start]
    while stack:
        n = stack.pop()
        if n in seen or n not in PASSAGES:
            continue
        seen.add(n)
        stack.extend(LINKS[n])
    return seen

def test_all_endings_reachable():
    seen = walk("Start")
    stranded = [p for p in PASSAGES
                if not p.startswith(("Story", "S-"))
                and p not in seen and p not in ORPHANS]
    assert stranded == [], f"stranded passages (no path from Start): {stranded}"

def test_all_scenes_routable():
    seen = walk("Start")
    missing = [s for s in SCENES if not any(s in p for p in seen)]
    assert missing == [], f"scenes not reachable from Start: {missing}"
