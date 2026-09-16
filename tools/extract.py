"""Parse glass.ni remark tables. Tables are 'Table of <Name>' followed by
tab-separated rows. Remark tables have columns starting/final/comment."""
import json, os, re, sys

REMARK_TABLES = ["Prologue Remarks", "Wondering Remarks", "Fitting Remarks",
    "Theodora Checking Remarks", "Lucinda Checking Remarks",
    "Cinderella Checking Remarks", "Reactions"]
LOOP_TABLES = {"Bad Bird Excuses": "loop", "Waiting": "loop",
    "Awwkwardness": "loop", "Insults": "loop", "Flattery": "loop"}

def extract_tables(text):
    tables, current, header = {}, None, None
    for line in text.splitlines():
        # NOTE: this matches every `Table of <Name>` declaration block, including
        # one-shot flavor tables consumed by `repeat through Table of ...` blanking
        # loops (Waiting, Lucinda Checks, Theodora Checks). Those are NOT
        # conversation tables: they never enter REMARK_TABLES/graph.json, but they
        # DO appear with row counts in extraction-report.json. Do not mistake the
        # `Lucinda Checks` / `Theodora Checks` report counts for missing content.
        m = re.match(r"Table of (.+)$", line.strip())
        if m:
            current = m.group(1).strip()
            tables[current] = []
            header = None
            continue
        if current is None or not line.strip():
            continue
        if header is None and "\t" in line:
            header = [h.strip().lower() for h in line.split("\t")]
            continue
        if header and "\t" in line:
            cells = line.split("\t")
            tables[current].append(dict(zip(header, [c.strip() for c in cells])))
    return tables

def apply_prune_rules(tables):
    kept = {k: list(v) for k, v in tables.items() if k in REMARK_TABLES}
    pruned = []
    for t in LOOP_TABLES:
        if t not in tables:
            continue
        n = len(tables[t])
        if n == 0:
            # Zero extracted rows: the table was dropped, not collapsed to a
            # representative passage (applies to Bad Bird Excuses).
            pruned.append({"table": t, "reason": "loop",
                           "detail": "0 rows, dropped (no representative passage)"})
        else:
            pruned.append({"table": t, "reason": "loop",
                           "detail": f"{n} rows collapsed to one representative passage"})
    return kept, pruned

import re as _re

def scan_bronze(text):
    # Rooms: `X is a room.` declarations plus directional `X is <dir> of Y`
    # declarations (Bronze declares most rooms relationally, e.g.
    # "The Central Courtyard is north of the Entrance Hall."). Both the
    # subject and the object of a relation name a room; names are runs of
    # capitalized words so compound "A is north of X and south of Y" lines
    # do not glue clauses together. Leading "The " is stripped and the
    # pronoun subject "It" is dropped.
    _name = r"[A-Z][\w\-']*(?: [A-Z][\w\-']*)*"
    _dirs = (r"north|south|east|west|northeast|northwest|southeast|"
             r"southwest|up|down|inside|outside")
    _found = set()
    for m in _re.finditer(r"^(" + _name + r") is a room\.", text, _re.M):
        _found.add(m.group(1).strip())
    for m in _re.finditer(
            r"^(" + _name + r") is (?:" + _dirs + r") (?:of|from) ", text, _re.M):
        _found.add(m.group(1).strip())
    for m in _re.finditer(
            r"\bis (?:" + _dirs + r") (?:of|from) the (" + _name + r")", text):
        _found.add(m.group(1).strip())
    rooms = sorted({_re.sub(r"^The ", "", r) for r in _found} - {"It"})
    tables = {}
    current, header = None, None
    for line in text.splitlines():
        m = _re.match(r"Table of (.+)$", line.strip())
        if m:
            current = m.group(1).strip()
            tables[current] = 0
            header = None
            continue
        if current is None or not line.strip():
            continue
        if header is None and "\t" in line:
            header = True
            continue
        if header and "\t" in line:
            tables[current] += 1
    return {"rooms": rooms, "tables": tables}

if __name__ == "__main__":
    if "--story" in sys.argv:
        try:
            kind = sys.argv[sys.argv.index("--story") + 1]
        except IndexError:
            kind = ""
        if kind == "bronze":
            src, out = sys.argv[1], sys.argv[2]
            text = open(src, encoding="utf-8", errors="replace").read()
            try:
                result = scan_bronze(text)
            except Exception as e:
                print(f"warning: bronze scan failed ({e}), skipping", file=sys.stderr)
                sys.exit(0)
            if not result["tables"]:
                print("warning: no bronze tables detected, skipping", file=sys.stderr)
                sys.exit(0)
            json.dump(result["rooms"], open(f"{out}/bronze-graph.json", "w"), indent=2)
            _prune_path = f"{out}/bronze-prune-list.json"
            if not os.path.exists(_prune_path):
                json.dump([], open(_prune_path, "w"), indent=2)
            json.dump(result["tables"],
                      open(f"{out}/bronze-extraction-report.json", "w"), indent=2)
            print(f"rooms={len(result['rooms'])} tables={len(result['tables'])} "
                  f"rows={sum(result['tables'].values())}")
            sys.exit(0)
    src, out = sys.argv[1], sys.argv[2]
    text = open(src, encoding="utf-8", errors="replace").read()
    tables = extract_tables(text)
    kept, pruned = apply_prune_rules(tables)
    json.dump(kept, open(f"{out}/graph.json", "w"), indent=2)
    json.dump(pruned, open(f"{out}/prune-list.json", "w"), indent=2)
    json.dump({k: len(v) for k, v in tables.items()},
              open(f"{out}/extraction-report.json", "w"), indent=2)
    print(f"tables={len(tables)} kept_rows={sum(len(v) for v in kept.values())} pruned={len(pruned)}")
