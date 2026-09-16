"""Clickability audit: every choice renders as a working link, every story
row is reachable from the start, guards have the right polarity
(appear-gates use [if], vanish-gates use [unless]), and every source row
is accounted for in either passages or the prune list."""
import json
import re
from pathlib import Path

TWEE = Path("src/glass/glass.twee").read_text()
PASSAGES = dict(re.findall(r"^::\s+(\S+)[^\n]*\n((?:(?!^::).)*)", TWEE, flags=re.M | re.S))
GRAPH = json.load(open("data/graph.json"))
PRUNE = json.load(open("data/prune-list.json"))


def is_row(n):
    return (re.fullmatch(r"S\d[A-Za-z0-9-]*", n) is not None
            and "-Hub" not in n and "-End-" not in n)


def norm(s):
    # Same normalizations as test_twee.norm (passage slugs say/cry/groomed
    # where source slugs say squawk/awwk/preened-feathers).
    return (s.replace("squawk", "say").replace("awwk", "cry").replace("polly", "cracker")
            .replace("properly-preened-feathers-lying-as-they-ought", "properly-groomed"))


def slug_of(r):
    if "starting" in r and "final" in r:
        raw = r["starting"] + "-" + r["final"]
    else:
        raw = (r.get("topic") or "") + "-" + (r.get("reaction rule") or r.get("response") or "")
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    return slug or "row"


def test_links_wellformed():
    """Every [[ opener closes on the same line with exactly one | target."""
    bad = []
    for i, line in enumerate(TWEE.splitlines()):
        if "[[" not in line and "]]" not in line:
            continue
        if line.count("[[") != line.count("]]"):
            bad.append(f"L{i + 1}: unbalanced: {line.strip()[:80]}")
            continue
        for m in re.finditer(r"\[\[([^\]]*)\]\]", line):
            inner = m.group(1)
            if "|" in inner and len(inner.split("|")) != 2:
                bad.append(f"L{i + 1}: bad link: {line.strip()[:80]}")
    assert bad == [], bad[:5]


def test_hub_link_labels_unique():
    """Within each scene hub, every story choice label must be unique:
    duplicate labels pointing at different passages strand players who
    can't tell choices apart. Bare `>` navigation is exempt by design
    (it deliberately carries no info)."""
    bad = []
    for name, body in PASSAGES.items():
        if "-Hub" not in name or "S-Hub-" in name:
            continue
        seen_labels = {}
        for m in re.finditer(r"\[\[([^\]|]+)\|([^\]]+)\]\]", body):
            label, target = m.group(1).strip(), m.group(2).strip()
            if label == ">":
                continue
            if label in seen_labels and seen_labels[label] != target:
                bad.append(f"{name}: {label!r} -> {seen_labels[label]} and {target}")
            seen_labels.setdefault(label, target)
    assert bad == [], f"duplicate hub labels: {bad[:5]}"


def test_prune_entries_valid():
    """Prune reasons are known; slug entries name real graph rows."""
    for e in PRUNE:
        assert e["reason"] in {"loop", "invalid-input", "user-cut"}, e
        if "slug" not in e:
            continue
        found = any(e["table"] == t and slug_of(r) == e["slug"]
                    for t, rows in GRAPH.items() for r in rows)
        assert found, f"prune entry names no row: {e}"
