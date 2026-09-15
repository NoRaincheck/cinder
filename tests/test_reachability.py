# tests/test_reachability.py
import re
from pathlib import Path

TWEE = Path("src/glass.twee").read_text()
PASSAGES = dict(re.findall(r"^::\s+(\S+)[^\n]*\n((?:(?!^::).)*)", TWEE, flags=re.M | re.S))
LINKS = {n: re.findall(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", b) for n, b in PASSAGES.items()}
SCENES = ["Prologue", "Wondering", "Fitting", "Checking-Theodora",
          "Checking-Lucinda", "Checking-Cinderella", "Theodora-Endgame",
          "Lucinda-Endgame", "End"]
ENDINGS = ["S9-End-Theodora-Marriage", "S9-End-Lucinda-Marriage", "S9-End-Peace",
           "S9-End-Disaster", "S9-End-Prince-Departs", "S9-End-Cinderella-Executed",
           "S9-End-Cinderella-Wed", "S9-End-Pirates"]

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
    seen = walk("Prologue-Intro")
    assert [e for e in ENDINGS if e not in seen] == []

def test_all_scenes_routable():
    seen = walk("Prologue-Intro")
    assert [s for s in SCENES if not any(s in p for p in seen)] == []
