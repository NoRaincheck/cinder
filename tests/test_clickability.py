"""Clickability audit: every choice renders as a working link, every story
row is reachable from the start, guards have the right polarity
(appear-gates use [if], vanish-gates use [unless]), and every source row
is accounted for in either passages or the prune list."""
import json
import re
from pathlib import Path

TWEE = Path("src/glass.twee").read_text()
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
    """Within each scene hub, every choice label must be unique: duplicate
    labels pointing at different passages (19x 'Steer toward more', 5x
    \"king's health\", ...) strand players who can't tell choices apart."""
    bad = []
    for name, body in PASSAGES.items():
        if "-Hub" not in name or "S-Hub-" in name:
            continue
        seen_labels = {}
        for m in re.finditer(r"\[\[([^\]|]+)\|([^\]]+)\]\]", body):
            label, target = m.group(1).strip(), m.group(2).strip()
            if label in seen_labels and seen_labels[label] != target:
                bad.append(f"{name}: {label!r} -> {seen_labels[label]} and {target}")
            seen_labels.setdefault(label, target)
    assert bad == [], f"duplicate hub labels: {bad[:5]}"


def test_guard_polarity():
    """Continue links appear ([if]); row links vanish ([unless]); funnels
    (checking->endgame, hub/ending navigation) stay unconditional."""
    gated_if, gated_unless, plain_cont = [], [], []
    for name, body in PASSAGES.items():
        lines = body.splitlines()
        for i, line in enumerate(lines):
            m = re.fullmatch(r"\[\[([^\]|]+)\|([^\]]+)\]\]", line.strip())
            if not m:
                continue
            prev = lines[i - 1].strip() if i > 0 else ""
            if m.group(1).startswith("Continue to ") and "endgame" not in m.group(1):
                assert prev.startswith("[if seen_"), f"{name}: gated continue misguarded: {prev!r}"
                gated_if.append(m.group(2))
            elif m.group(1).startswith("Continue to "):
                assert not prev.startswith("[") or prev == "[if 2 + 2 === 4]", \
                    f"{name}: funnel continue guarded: {prev!r}"
                plain_cont.append(m.group(2))
            elif m.group(2) in PASSAGES and is_row(m.group(2)):
                assert prev.startswith("[unless seen_"), f"{name}: row link misguarded: {prev!r}"
                gated_unless.append(m.group(2))
    assert len(gated_if) == 5, gated_if
    assert sorted(plain_cont) == ["S7-Theodora-Endgame-Hub", "S8-Lucinda-Endgame-Hub"]
    assert len(gated_unless) == 15, len(gated_unless)


def test_all_rows_reachable_from_start():
    """Static walk from Prologue-Intro must visit every non-pruned row."""
    links = {n: re.findall(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", b)
             for n, b in PASSAGES.items()}
    seen, stack = set(), ["Prologue-Intro"]
    while stack:
        n = stack.pop()
        if n in seen or n not in PASSAGES:
            continue
        seen.add(n)
        stack.extend(links[n])
    pruned = {(e["table"], e.get("slug")) for e in PRUNE if "slug" in e}
    missing = []
    for table, rows in GRAPH.items():
        for r in rows:
            slug = slug_of(r)
            if (table, slug) in pruned:
                continue
            if not any(norm(slug) in norm(p.lower()) for p in seen):
                missing.append(f"{table}:{slug}")
    assert missing == [], f"unreachable rows: {missing[:5]}"


def test_source_rows_accounted():
    """Every graph row resolves to a passage or a prune-list pair entry."""
    pruned = {(e["table"], e.get("slug")) for e in PRUNE if "slug" in e}
    whole = {e["table"] for e in PRUNE if "slug" not in e}
    orphans = []
    for table, rows in GRAPH.items():
        for r in rows:
            slug = slug_of(r)
            ok = any(norm(slug) in norm(p.lower()) for p in PASSAGES if is_row(p))
            if not ok and (table, slug) not in pruned and table not in whole:
                orphans.append(f"{table}:{slug}")
    assert orphans == [], f"source rows with no passage and no prune entry: {orphans[:5]}"


def test_prune_entries_valid():
    """Prune reasons are known; slug entries name real graph rows."""
    for e in PRUNE:
        assert e["reason"] in {"loop", "invalid-input", "user-cut"}, e
        if "slug" not in e:
            continue
        found = any(e["table"] == t and slug_of(r) == e["slug"]
                    for t, rows in GRAPH.items() for r in rows)
        assert found, f"prune entry names no row: {e}"
