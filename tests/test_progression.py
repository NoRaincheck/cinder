"""Scene gating: the story arc is Prologue -> Wondering -> Fitting ->
Checking T/L/C -> Endgames, with each ending homed to exactly one scene.
The start passage opens only the Prologue; later scenes unlock behind
key-row seen-flags; checking scenes funnel forward into endgames."""
import re
from pathlib import Path

TWEE = Path("src/glass.twee").read_text()
PASSAGES = dict(re.findall(r"^::\s+(\S+)[^\n]*\n((?:(?!^::).)*)", TWEE, flags=re.M | re.S))

HOMES = {
    "S1-Prologue-Hub": {"S9-End-Pirates"},
    "S2-Wondering-Hub": {"S9-End-Prince-Departs"},
    "S3-Fitting-Hub": {"S9-End-Disaster"},
    "S4-Checking-Theodora-Hub": set(),
    "S5-Checking-Lucinda-Hub": set(),
    "S6-Checking-Cinderella-Hub": {"S9-End-Peace", "S9-End-Cinderella-Executed",
                                   "S9-End-Cinderella-Wed"},
    "S7-Theodora-Endgame-Hub": {"S9-End-Theodora-Marriage"},
    "S8-Lucinda-Endgame-Hub": {"S9-End-Lucinda-Marriage"},
}

# (hub, guard-or-None, label, target)
CONTINUES = [
    ("S1-Prologue-Hub", "[unless seen_s1_prologue_blank_shoe_1]",
     "Continue to the Wondering talk", "S2-Wondering-Hub"),
    ("S2-Wondering-Hub", "[unless seen_s2_wondering_blank_ball_1]",
     "Continue to the Fitting talk", "S3-Fitting-Hub"),
    ("S3-Fitting-Hub", "[unless seen_s3_fitting_blank_theo_1]",
     "Continue to Checking Theodora", "S4-Checking-Theodora-Hub"),
    ("S3-Fitting-Hub", "[unless seen_s3_fitting_blank_theo_1]",
     "Continue to Checking Lucinda", "S5-Checking-Lucinda-Hub"),
    ("S3-Fitting-Hub", "[unless seen_s3_fitting_blank_theo_1]",
     "Continue to Checking Cinderella", "S6-Checking-Cinderella-Hub"),
    ("S4-Checking-Theodora-Hub", None,
     "Continue to Theodora's endgame", "S7-Theodora-Endgame-Hub"),
    ("S5-Checking-Lucinda-Hub", None,
     "Continue to Lucinda's endgame", "S8-Lucinda-Endgame-Hub"),
]


def links_of(name):
    return re.findall(r"\[\[([^\]|]+)\|([^\]]+)\]\]", PASSAGES[name])


def test_intro_opens_only_prologue():
    links = links_of("Prologue-Intro")
    hubs = [t for _, t in links if t.endswith("-Hub")]
    assert hubs == ["S1-Prologue-Hub"], f"intro leaks scenes: {hubs}"
    assert not [t for _, t in links if "-End-" in t], "intro links endings directly"


def test_ending_homes():
    for hub, want in HOMES.items():
        got = {t for _, t in links_of(hub) if "-End-" in t}
        assert got == want, f"{hub}: endings {sorted(got)} != {sorted(want)}"
    homed = sorted(e for want in HOMES.values() for e in want)
    assert len(homed) == 8 and len(set(homed)) == 8, f"endings lost/duplicated: {homed}"


def test_continue_chain():
    for hub, guard, label, target in CONTINUES:
        lines = PASSAGES[hub].splitlines()
        try:
            i = next(i for i, l in enumerate(lines)
                     if l.strip() == f"[[{label}|{target}]]")
        except StopIteration:
            raise AssertionError(f"{hub}: missing continue link [[{label}|{target}]]")
        if guard is None:
            continue  # checking->endgame funnels stay unconditional
        assert lines[i - 1].strip() == guard, \
            f"{hub}: continue link misguarded: {lines[i - 1].strip()!r}"
        assert guard.startswith("[unless seen_"), guard


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
