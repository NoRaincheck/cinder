"""Parse story.ni remark tables. Tables are 'Table of <Name>' followed by
tab-separated rows. Remark tables have columns starting/final/comment."""
import json, re, sys

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
            if line.strip() == "" and current:
                pass
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

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    text = open(src, encoding="utf-8", errors="replace").read()
    tables = extract_tables(text)
    kept, pruned = apply_prune_rules(tables)
    json.dump(kept, open(f"{out}/graph.json", "w"), indent=2)
    json.dump(pruned, open(f"{out}/prune-list.json", "w"), indent=2)
    json.dump({k: len(v) for k, v in tables.items()},
              open(f"{out}/extraction-report.json", "w"), indent=2)
    print(f"tables={len(tables)} kept_rows={sum(len(v) for v in kept.values())} pruned={len(pruned)}")
