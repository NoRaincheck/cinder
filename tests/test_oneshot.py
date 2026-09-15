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
    assert len(rows) == 104
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
    assert count == 104, f"guarded row links changed: {count}"
    assert bad == [], f"unguarded row links: {bad[:5]}"


def test_guards_reference_defined_vars():
    defined = {var_of(n) for n in PASSAGES if is_row(n)}
    used = set(re.findall(r"^\[unless (seen_[a-z0-9_]+)\]$", TWEE, flags=re.M))
    assert used - defined == set(), f"guards with no defining passage: {sorted(used - defined)[:5]}"
    assert defined - used == set(), f"flags set but never used: {sorted(defined - used)[:5]}"


def test_hubs_endings_intro_unguarded():
    # Designated Continue links are the one exception: they must be guarded
    # (scene gating) and are audited in test_progression.py instead.
    bad = []
    for name, body in PASSAGES.items():
        prev = ""
        for line in body.splitlines():
            m = re.fullmatch(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", line.strip())
            if m and m.group(1) in PASSAGES and not is_row(m.group(1)):
                lm = re.match(r"\[\[([^\]|]+)\|", line.strip())
                label = lm.group(1) if lm else ""
                guarded = (prev.startswith("[unless ") or prev.startswith("[if ")) \
                    and prev != "[if 2 + 2 === 4]"
                if guarded and not label.startswith("Continue to "):
                    bad.append(f"{name}: {line.strip()[:60]}")
            prev = line.strip()
    assert bad == [], f"guarded hub/ending/intro links (dead-end risk): {bad[:5]}"


def test_guard_scope_terminated():
    """Chapbook applies a modifier to ALL following text until the next
    modifier (engine render loop resets its accumulator only per text
    block). So a trailing [unless] would hide every unguarded link below
    it. Every guard's scope must therefore hold exactly its own link:
    guards come in guard+link pairs, and runs end with the always-true
    `[if 2 + 2 === 4]` terminator before any unguarded content."""
    LINK = re.compile(r"^\[\[(?:[^|\]]+\|)?([^\]]+)\]\]$")
    SENTINEL = "[if 2 + 2 === 4]"
    bad = []
    for name, body in PASSAGES.items():
        lines = body.splitlines()
        n_guards = sum(1 for l in lines if l.strip().startswith("[unless ")
                       or (l.strip().startswith("[if ") and l.strip() != SENTINEL))
        if n_guards:
            assert sum(1 for l in lines if l.strip() == SENTINEL) == 1, \
                f"{name}: guarded passage without exactly one scope terminator"
        for i, line in enumerate(lines):
            s = line.strip()
            if s == SENTINEL or not (s.startswith("[unless ") or s.startswith("[if ")):
                continue
            scope, k = [], i + 1
            while k < len(lines):
                t = lines[k].strip()
                if t == "":
                    k += 1
                    continue
                if t.startswith("[") and not t.startswith("[["):
                    break
                scope.append(t)
                k += 1
            if len(scope) != 1 or not LINK.match(scope[0]):
                bad.append(f"{name}: {s} scope={scope[:2]}")
    assert bad == [], f"leaking guard scopes: {bad[:5]}"
