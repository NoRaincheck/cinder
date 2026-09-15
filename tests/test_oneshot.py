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
    assert len(rows) == 15
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
    assert count == 15, f"guarded row links changed: {count}"
    assert bad == [], f"unguarded row links: {bad[:5]}"


def test_guards_reference_defined_vars():
    defined = {var_of(n) for n in PASSAGES if is_row(n)}
    used = set(re.findall(r"^\[(?:unless|if) (seen_s\d[a-z0-9_]+)\]$", TWEE, flags=re.M))
    assert used - defined == set(), f"guards with no defining passage: {sorted(used - defined)[:5]}"
    assert defined - used == set(), f"flags set but never used: {sorted(defined - used)[:5]}"


def test_start_passage_initializes_all_seen_vars():
    """Chapbook evaluates [if seen_*] as raw JS and throws ReferenceError on
    undefined vars (no auto-false). Prologue-Intro runs first and must default
    every seen_* used anywhere, with a typeof-guard so revisits preserve true."""
    used = set(re.findall(r"^\[(?:unless|if) (seen_[a-z0-9_]+)\]$", TWEE, flags=re.M))
    body = PASSAGES["Prologue-Intro"]
    assert "\n--\n" in body, "Prologue-Intro missing vars section (undefined-var crash)"
    vars_section = body.split("\n--\n", 1)[0]
    initialized = set(re.findall(r"^(seen_[a-z0-9_]+)\s*:", vars_section, flags=re.M))
    assert used - initialized == set(), \
        f"seen vars used but never initialized at start: {sorted(used - initialized)[:5]}"


def test_hubs_endings_intro_unguarded():
    # Designated Continue links are the one exception: they must be guarded
    # (scene gating) and are audited in test_progression.py instead.
    # S-Hub-* links are the other exception: visited-state quads audited in
    # test_hubstrike.py. Everything else hub/ending-bound stays unconditional.
    bad = []
    for name, body in PASSAGES.items():
        prev = ""
        for line in body.splitlines():
            m = re.fullmatch(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", line.strip())
            if m and m.group(1) in PASSAGES and not is_row(m.group(1)) \
                    and not m.group(1).startswith("S-Hub-"):
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
    block). So a trailing guard would hide every unguarded link below it.
    Legal shapes and their exact scopes:
    - `[unless seen_*]` / `[if seen_*]` + one link line (row/continue gates)
    - `[if seen_hub_*]` + one struck-text line, then `[else]` + one link
      (visited-state hub quads)
    - `[if 2 + 2 === 4]` scope terminator before trailing unguarded content.
    """
    LINK = re.compile(r"^\[\[(?:[^|\]]+\|)?([^\]]+)\]\]$")
    SENTINEL = "[if 2 + 2 === 4]"
    bad = []
    for name, body in PASSAGES.items():
        lines = [l for l in body.splitlines()]

        def is_mod(s):
            return s.startswith("[") and not s.startswith("[[")

        i = 0
        while i < len(lines):
            s = lines[i].strip()
            if s == SENTINEL or not (s.startswith("[unless ") or s.startswith("[if ")
                                    or s == "[else]"):
                i += 1
                continue
            scope, k = [], i + 1
            while k < len(lines):
                t = lines[k].strip()
                if t == "":
                    k += 1
                    continue
                if is_mod(t):
                    break
                scope.append(t)
                k += 1
            if re.match(r"\[if (seen_hub_[a-z0-9_]+)\]$", s):
                if len(scope) != 1 or LINK.match(scope[0]):
                    bad.append(f"{name}: {s} scope={scope[:2]}")
                    i += 1
                    continue
                nxt = lines[k].strip() if k < len(lines) else ""
                if not nxt == "[else]":
                    bad.append(f"{name}: {s} not followed by [else]: {nxt[:40]}")
            else:
                if len(scope) != 1 or not LINK.match(scope[0]):
                    bad.append(f"{name}: {s} scope={scope[:2]}")
            i += 1
    assert bad == [], f"leaking guard scopes: {bad[:5]}"
