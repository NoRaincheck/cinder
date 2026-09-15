"""Visited-state hub links: every `S-Hub-*` link renders as an
`[if seen_hub_*]` / struck-text / `[else]` / link quad, so visited hubs
show struck-through instead of staying re-clickable (hiding them would
empty hub pages and strand players). Scene hubs, intro, endings, and
funnels stay always-clickable: revisiting those is load-bearing."""
import re
from pathlib import Path

TWEE = Path("src/glass.twee").read_text()
PASSAGES = dict(re.findall(r"^::\s+(\S+)[^\n]*\n((?:(?!^::).)*)", TWEE, flags=re.M | re.S))


def hub_flag(target):
    return "seen_hub_" + target[len("S-Hub-"):].lower().replace("-", "_")


def test_hub_flags_defined():
    hubs = sorted(n for n in PASSAGES if re.fullmatch(r"S-Hub-[A-Za-z0-9-]+", n))
    assert len(hubs) == 13, hubs
    bad = [h for h in hubs
           if not PASSAGES[h].startswith(f"{hub_flag(h)}: true\n--\n")]
    assert bad == [], f"hubs missing leading vars section: {bad}"


def test_hub_flags_used_consistently():
    defined = {hub_flag(h) for h in PASSAGES if re.fullmatch(r"S-Hub-[A-Za-z0-9-]+", h)}
    used = set(re.findall(r"^\[if (seen_hub_[a-z0-9_]+)\]$", TWEE, flags=re.M))
    assert used - defined == set(), f"hub guards with no hub: {sorted(used - defined)[:5]}"
    assert defined - used == set(), f"hub flags never used: {sorted(defined - used)[:5]}"


def test_hub_links_quadformed():
    """Every S-Hub link line is the tail of an if/struck/else/link quad."""
    bad, count = [], 0
    for name, body in PASSAGES.items():
        lines = body.splitlines()
        for i, line in enumerate(lines):
            m = re.fullmatch(r"\[\[([^\]|]+)\|(S-Hub-[^\]]+)\]\]", line.strip())
            if not m:
                continue
            count += 1
            label, target = m.group(1), m.group(2)
            want = [f"[if {hub_flag(target)}]", f"~~{label}~~", "[else]"]
            got = [lines[j].strip() if j >= 0 else "" for j in (i - 3, i - 2, i - 1)]
            if got != want:
                bad.append(f"{name}: {line.strip()[:60]} prev={got}")
    assert count == 1638, f"hub link count changed: {count}"
    assert bad == [], f"non-quad hub links: {bad[:5]}"


def test_scene_hubs_not_struck():
    """Struck text appears only inside hub quads (one per hub link): scene
    hubs, intro, endings, and funnels must stay unconditionally clickable."""
    struck = re.findall(r"^~~(.+)~~$", TWEE, flags=re.M)
    assert len(struck) == 1638, len(struck)
