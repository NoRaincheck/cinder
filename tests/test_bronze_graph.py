import re
from pathlib import Path

SRC = Path("src/bronze/bronze.twee")
ENDINGS = ["End-Bronze-Leave", "End-Bronze-Stay", "End-Bronze-Beast"]


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
    seen, stack = set(), ["Bronze-Start"]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(links.get(node, []))
    for end in ENDINGS:
        assert end in seen, f"{end} unreachable from Bronze-Start"


def test_passage_budget():
    names, _ = parse_passages(SRC.read_text())
    story = [n for n in names if n not in ("StoryTitle", "StoryData")]
    assert len(story) == 28, f"expected 28 story passages, got {len(story)}"


def test_guarded_vars_initialized_at_start():    # Chapbook throws ReferenceError for [unless X] when X was never
    # declared. Every guarded var must be initialized in Bronze-Start
    # (the StoryData start passage), mirroring Glass Start's init block.
    text = SRC.read_text()
    bodies = re.split(r"^::\s+\S+", text, flags=re.M)
    names = re.findall(r"^::\s+(\S+)", text, re.M)
    start_body = bodies[names.index("Bronze-Start") + 1]
    guarded = set(re.findall(r"\[(?:if|unless) (seen_\w+)\]", text))
    assert guarded, "no guarded vars found"
    for var in sorted(guarded):
        assert re.search(rf"^{var}: false", start_body, re.M), (
            f"{var} guarded but not initialized in Bronze-Start"
        )


def test_hubs_never_empty():
    # Hub pages must never empty out: every passage ending with the hub
    # closer needs at least one UNGUARDED link, so no play state can
    # strand the player with zero visible links.
    text = SRC.read_text()
    bodies = re.split(r"^::\s+\S+", text, flags=re.M)[1:]
    names = re.findall(r"^::\s+(\S+)", text, re.M)
    for name, body in zip(names, bodies):
        if "waits for your next move" not in body:
            continue
        pending = 0
        open_links = 0
        for ln in body.splitlines():
            if re.match(r"\[unless seen_\w+\]", ln.strip()):
                pending += 1
                continue
            if re.search(r"\[\[.*?\|.*?\]\]", ln):
                if pending == 0:
                    open_links += 1
                pending = 0
        assert open_links >= 1, f"{name} can empty out (no unguarded link)"


def test_seen_markers():
    # Hubstrike design: no hidden one-shot links remain, and no per-link
    # markers either — each hub carries a recap list of its own seen
    # discoveries instead (see test_scene_recaps).
    text = SRC.read_text()
    assert "[unless" not in text, "hidden one-shot guards remain"
    assert "(seen)" not in text, "per-link seen markers remain"


# Hub -> discovery targets it must recap (outbound one-shots reachable
# from that hub). Rose-Garden, one-shot interiors, Choices, and endings
# have no scene-relevant discoveries: no recap.
RECAP_MAP = {
    "Bronze-Start": ["seen_bronze_gate"],
    "Bronze-Courtyard": ["seen_bronze_helical_stair"],
    "Bronze-Scarlet-Gallery": [
        "seen_bronze_scarlet_tower",
        "seen_bronze_history_gallery",
        "seen_bronze_treasure_room",
    ],
    "Bronze-Scarlet-Tower": ["seen_bronze_helmet"],
    "Bronze-History-Gallery": ["seen_bronze_maze_room"],
    "Bronze-Treasure-Room": ["seen_bronze_cage"],
    "Bronze-Maze-Room": ["seen_bronze_bear_corridor"],
    "Bronze-Bear-Corridor": ["seen_bronze_zoo"],
    "Bronze-Zoo": ["seen_bronze_beast"],
    "Bronze-Law-Library": [
        "seen_bronze_contract_book",
        "seen_bronze_records_room",
        "seen_bronze_crypt_door",
    ],
    "Bronze-Rotunda": ["seen_bronze_hourglass"],
    "Bronze-Hourglass": ["seen_bronze_records_room"],
}


def test_scene_recaps():
    text = SRC.read_text()
    assert "[end if" not in text, "[end if] is invalid Chapbook"
    names = re.findall(r"^::\s+(\S+)", text, re.M)
    bodies = re.split(r"^::\s+\S+", text, flags=re.M)[1:]
    by_name = dict(zip(names, bodies))
    for hub, want in RECAP_MAP.items():
        body = by_name[hub]
        # Recap blocks precede the first link of the passage.
        pre_links = body.split("[[")[0]
        found = re.findall(
            r"^\[if (seen_\w+)\]\n\*\((seen: .+)\)\*\n\[continue\]$",
            pre_links,
            re.M,
        )
        assert [v for v, _ in found] == want, (
            f"{hub}: recap mismatch got={[v for v, _ in found]} want={want}"
        )
    # No recap anywhere else (one-shots, Choices, endings, Rose-Garden).
    all_recaps = 0
    for name, body in by_name.items():
        n = len(re.findall(r"^\[if (seen_\w+)\]\n\*\((seen: .+)\)\*\n\[continue\]$", body, re.M))
        all_recaps += n
        if name not in RECAP_MAP:
            assert n == 0, f"{name} has unexpected recap"
    assert all_recaps == sum(len(v) for v in RECAP_MAP.values())
