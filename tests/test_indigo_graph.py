import json
import re
from pathlib import Path

SRC = Path("src/indigo/indigo.twee")
GRAPH = json.loads(Path("data/indigo-graph.json").read_text())
FLAGS = ["seen_indigo_month", "seen_indigo_potion", "seen_indigo_hair_strong",
         "seen_indigo_candle", "seen_indigo_hour", "seen_indigo_candle_lit",
         "seen_indigo_decade", "seen_indigo_hair_long", "seen_indigo_braid",
         "seen_indigo_millennium", "seen_indigo_window_aged"]
RECAP_MAP = {
    "Indigo-Kitchen": ["seen_indigo_month", "seen_indigo_hair_strong", "seen_indigo_candle_lit"],
    "Indigo-Blue-Tower": ["seen_indigo_candle", "seen_indigo_braid", "seen_indigo_window_aged"],
    "Indigo-Store-Room": ["seen_indigo_millennium"],
}


def parse_passages(text):
    names = re.findall(r"^::\s+(\S+)", text, re.M)
    links = {}
    bodies = re.split(r"^::\s+\S+", text, flags=re.M)[1:]
    for name, body in zip(names, bodies):
        links[name] = re.findall(r"\[\[.*?\|(.*?)\]\]", body)
    return names, links


def test_no_dead_links():
    names, links = parse_passages(SRC.read_text())
    for src, targets in links.items():
        for t in targets:
            assert t in names, f"{src} links to missing {t}"


def test_endings_reachable():
    names, links = parse_passages(SRC.read_text())
    seen, stack = set(), ["Indigo-Start"]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(links.get(node, []))
    for end in GRAPH["endings"]:
        assert end in seen, f"{end} unreachable from Indigo-Start"
    assert set(names) - {"StoryTitle", "StoryData"} <= seen, "stranded passages"


def test_passage_budget():
    names, _ = parse_passages(SRC.read_text())
    story = [n for n in names if n not in ("StoryTitle", "StoryData")]
    assert len(story) == 20, f"expected 20 story passages, got {len(story)}"
    assert sorted(story) == sorted(GRAPH["passages"])


def test_guarded_vars_initialized_at_start():
    text = SRC.read_text()
    bodies = re.split(r"^::\s+\S+", text, flags=re.M)
    names = re.findall(r"^::\s+(\S+)", text, re.M)
    start_body = bodies[names.index("Indigo-Start") + 1]
    guarded = set(re.findall(r"\[if (seen_\w+)\]", text))
    assert sorted(guarded) == sorted(FLAGS), f"flag mismatch: {sorted(guarded)}"
    for var in FLAGS:
        assert re.search(rf"^{var}: false", start_body, re.M), (
            f"{var} guarded but not initialized in Indigo-Start"
        )


def test_no_unless_guards():
    assert "[unless" not in SRC.read_text(), "unless-guards are not the house idiom"


def test_hubs_never_empty():
    text = SRC.read_text()
    bodies = re.split(r"^::\s+\S+", text, flags=re.M)[1:]
    names = re.findall(r"^::\s+(\S+)", text, re.M)
    for name, body in zip(names, bodies):
        if "The tower waits for your next move." not in body:
            continue
        assert re.search(r"\[\[.*?\|.*?\]\]", body), f"{name} has no link at all"


def test_unguarded_choice_cap():
    # At most 3 unguarded story links per passage; [if]-gated progression
    # links and bare `>` nav are exempt.
    text = SRC.read_text()
    bodies = re.split(r"^::\s+\S+", text, flags=re.M)[1:]
    names = re.findall(r"^::\s+(\S+)", text, re.M)
    for name, body in zip(names, bodies):
        if name in ("StoryTitle", "StoryData"):
            continue
        pending_gate = False
        unguarded = 0
        for ln in body.splitlines():
            s = ln.strip()
            if re.fullmatch(r"\[if seen_\w+\]", s):
                pending_gate = True
                continue
            m = re.fullmatch(r"\[\[([^\]|]+)\|([^\]]+)\]\]", s)
            if not m:
                continue
            if m.group(1).strip() == ">":
                pending_gate = False
                continue
            if not pending_gate:
                unguarded += 1
            pending_gate = False
        assert unguarded <= 3, f"{name} shows {unguarded} unguarded story links"


def test_scene_recaps():
    text = SRC.read_text()
    assert "[end if" not in text, "[end if] is invalid Chapbook"
    names = re.findall(r"^::\s+(\S+)", text, re.M)
    bodies = re.split(r"^::\s+\S+", text, flags=re.M)[1:]
    by_name = dict(zip(names, bodies))
    for hub, want in RECAP_MAP.items():
        pre_links = by_name[hub].split("[[")[0]
        found = re.findall(r"^\[if (seen_\w+)\]\n\*\((seen: .+)\)\*\n\[continue\]$", pre_links, re.M)
        assert [v for v, _ in found] == want, f"{hub}: recap mismatch"
