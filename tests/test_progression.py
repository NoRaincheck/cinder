"""Scene ordering for the curated 3-choice spine (2026-09-15): the arc runs
Prologue -> Wondering -> Fitting -> Checking -> endings. The hub-based scene
gating, ending-homes map, and continue-link guards were removed in the
curation; the one remaining audit checks that no row passage links across
scenes (scene membership is inferred from the passage-name prefix)."""
import re
from pathlib import Path

TWEE = Path("src/glass.twee").read_text()
PASSAGES = dict(re.findall(r"^::\s+(\S+)[^\n]*\n((?:(?!^::).)*)", TWEE, flags=re.M | re.S))

def test_no_scene_skipping():
    """No row passage links outside its own scene (hubs/endings/intro free)."""
    def scene(n):
        m = re.match(r"S(\d)-", n)
        return m.group(1) if m else None
    bad = []
    for name, body in PASSAGES.items():
        here = scene(name)
        if here is None or "-Hub" in name or "-End-" in name:
            continue
        for _, t in re.findall(r"\[\[([^\]|]+)\|([^\]]+)\]\]", body):
            there = scene(t)
            if there is not None and "-Hub" not in t and "-End-" not in t and there != here:
                bad.append(f"{name} -> {t}")
    assert bad == [], f"cross-scene row links: {bad[:5]}"
