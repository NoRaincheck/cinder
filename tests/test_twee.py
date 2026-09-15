import json, re
from pathlib import Path

TWEE = Path("src/glass.twee").read_text()
PASSAGES = dict(re.findall(r"^::\s+(\S+)[^\n]*\n((?:(?!^::).)*)", TWEE, flags=re.M | re.S))
LINKS = {name: re.findall(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", body) for name, body in PASSAGES.items()}
GRAPH = json.load(open("data/graph.json"))
PRUNE = json.load(open("data/prune-list.json"))
SUBJECTS = ["kings-health", "heirs", "marriage", "ball", "shoe", "cinderella",
            "theo", "lucinda", "stepmother", "love", "blood", "magic", "god", "birds"]
# Twee metadata passages carry no game links by definition; exempt from link/body rules.
META = {"StoryTitle", "StoryData"}

def slug_of(r):
    if "starting" in r and "final" in r:
        raw = r["starting"] + "-" + r["final"]
    else:
        # Reactions table has topic/response/reaction-rule keys instead.
        raw = (r.get("topic") or "") + "-" + (r.get("reaction rule") or r.get("response") or "")
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    return slug or "row"

def test_no_missing_rows():
    missing = []
    for table, rows in GRAPH.items():
        for r in rows:
            slug = slug_of(r)
            if not any(slug in p.lower() for p in PASSAGES):
                missing.append(f"{table}:{slug}")
    pruned_slugs = json.dumps(PRUNE)
    missing = [m for m in missing if m.split(":")[0] not in pruned_slugs]
    assert missing == [], f"rows with no passage: {missing[:5]}"

def test_link_targets_exist():
    bad = [(p, t) for p, ts in LINKS.items() for t in ts if t not in PASSAGES]
    assert bad == [], f"dead links: {bad[:5]}"

def test_every_conversation_passage_links_all_subjects():
    weak = [p for p, ts in LINKS.items()
            if p.startswith("S") and "-End-" not in p and p not in META
            and sum(1 for s in SUBJECTS if any(s in t.lower() for t in ts)) < len(SUBJECTS)]
    assert weak == [], f"passages missing subject choices: {weak[:5]}"

def test_fidelity_verbatim():
    thin = [p for p, b in PASSAGES.items()
            if p.startswith("S") and p not in META and len(b.strip()) < 80]
    assert thin == [], f"passages too thin (LLM invented?): {thin[:5]}"
    bad = []
    for table, rows in GRAPH.items():
        for r in rows:
            slug = slug_of(r)
            if not slug:
                continue
            cands = [p for p in PASSAGES
                     if p.startswith("S") and p not in META and slug in p.lower()]
            if not cands:
                continue  # row-to-passage coverage is asserted by test_no_missing_rows
            if "comment" in r:
                src = r["comment"] or ""
            else:
                # Reactions rows use topic/response keys.
                src = " ".join([r.get("topic") or "", r.get("response") or ""])
            src = " ".join(src.split())
            if not any(src[i:i + 40] in " ".join(PASSAGES[p].split())
                       for p in cands for i in range(len(src) - 39)):
                bad.append(f"{table}:{slug}")
    assert bad == [], f"passages lacking a >=40-char verbatim run: {bad[:10]} (total {len(bad)})"
