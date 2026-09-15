"""One-shot links: every story row sets a seen-flag in a leading vars section,
every link to a row is hidden behind an [unless seen_*] guard, and hub /
ending / intro navigation stays unconditional (no dead ends by removal)."""
import re
from pathlib import Path

TWEE = Path("src/glass.twee").read_text()
PASSAGES = dict(re.findall(r"^::\s+(\S+)[^\n]*\n((?:(?!^::).)*)", TWEE, flags=re.M | re.S))
META = {"StoryTitle", "StoryData"}


def is_row(n):
    return (re.fullmatch(r"S\d[A-Za-z0-9-]*", n) is not None
            and "-Hub" not in n and "-End-" not in n)


def var_of(n):
    return "seen_" + n.lower().replace("-", "_")


def test_row_passages_set_seen_flag():
    rows = [n for n in PASSAGES if is_row(n)]
    assert len(rows) == 107
    bad = [n for n in rows
           if not PASSAGES[n].startswith(f"{var_of(n)}: true\n--\n")]
    assert bad == [], f"row passages missing leading vars section: {bad[:5]}"


def test_row_links_guarded():
    bad, count = [], 0
    for name, body in PASSAGES.items():
        prev = ""
        for line in body.splitlines():
            m = re.fullmatch(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", line.strip())
            if m and m.group(1) in PASSAGES and is_row(m.group(1)):
                count += 1
                if prev != f"[unless {var_of(m.group(1))}]":
                    bad.append(f"{name}: {line.strip()[:60]}")
            prev = line.strip()
    assert count == 110, f"guarded row links changed: {count}"
    assert bad == [], f"unguarded row links: {bad[:5]}"


def test_guards_reference_defined_vars():
    defined = {var_of(n) for n in PASSAGES if is_row(n)}
    used = set(re.findall(r"^\[unless (seen_[a-z0-9_]+)\]$", TWEE, flags=re.M))
    assert used - defined == set(), f"guards with no defining passage: {sorted(used - defined)[:5]}"
    assert defined - used == set(), f"flags set but never used: {sorted(defined - used)[:5]}"


def test_hubs_endings_intro_unguarded():
    bad = []
    for name, body in PASSAGES.items():
        prev = ""
        for line in body.splitlines():
            m = re.fullmatch(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", line.strip())
            if m and m.group(1) in PASSAGES and not is_row(m.group(1)):
                if prev.startswith("[unless ") or prev.startswith("[if "):
                    bad.append(f"{name}: {line.strip()[:60]}")
            prev = line.strip()
    assert bad == [], f"guarded hub/ending/intro links (dead-end risk): {bad[:5]}"
