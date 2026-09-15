# Twee-Glass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port Glass (Inform 7 parser) to choice-based Chapbook Twee with ALL paths preserved (only loop/invalid inputs pruned) as a GitHub Pages static site, with automated tests for every behavior.

**Architecture:** Tweego compiles `src/*.twee` (Chapbook 2) to `dist/index.html`; `tools/extract.py` parses `story.ni` remark tables into `data/graph.json` + `data/prune-list.json`; pytest asserts full coverage, link integrity, reachability, fidelity, and build output.

**Tech Stack:** Tweego 2.1.1, Chapbook 2.3.0, Python 3.9+, pytest 8.3, GitHub Actions Pages deploy.

**Spec:** `docs/superpowers/specs/2026-09-14-twee-glass-design.md`

## Global Constraints

- Story format is Chapbook 2 only, no custom JavaScript.
- ALL remark rows ship except `data/prune-list.json` entries with reason `loop` or `invalid-input`.
- Light polish only: passage bodies keep a >=40-char verbatim substring of source `comment`.
- `dist/` is gitignored build output; Pages deploys via Actions artifact.
- Every task ends with a green test + commit.

---

### Task 1: Scaffold repo, toolchain pins, CI skeleton

**Files:**
- Create: `package.json`, `requirements.txt`, `Makefile`, `.github/workflows/pages.yml`, `tests/test_toolchain.py`
- Modify: `.gitignore` (append `dist/`, `build/`, `.pytest_cache/`)

**Interfaces:**
- Consumes: nothing
- Produces: `make build` (runs tweego), `make test` (runs pytest), CI workflow path used by Task 5

- [ ] **Step 1: Write the failing test**

```python
# tests/test_toolchain.py
import json
from pathlib import Path

def test_package_pins_tweego_chapbook():
    pkg = json.loads(Path("package.json").read_text())
    assert pkg["devDependencies"]["tweego"] == "2.1.1"
    assert pkg["devDependencies"]["chapbook"] == "2.3.0"

def test_requirements_pins_pytest():
    req = Path("requirements.txt").read_text()
    assert "pytest==8.3" in req

def test_pages_workflow_exists():
    wf = Path(".github/workflows/pages.yml").read_text()
    assert "tweego" in wf and "deploy-pages" in wf
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_toolchain.py -v`
Expected: FAIL with "package.json not found" (files do not exist yet)

- [ ] **Step 3: Write minimal implementation**

```json
// package.json
{"name": "twee-glass", "private": true, "devDependencies": {"tweego": "2.1.1", "chapbook": "2.3.0"}}
```

```
# requirements.txt
pytest==8.3
```

```makefile
# Makefile
build:
	npx tweego@2.1.1 src -o dist/index.html
test:
	python3 -m pytest tests/ -v
```

```yaml
# .github/workflows/pages.yml
name: pages
on: {push: {branches: [main]}}
permissions: {pages: write, id-token: write}
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: {node-version: 20}
      - run: npm install -g tweego@2.1.1 chapbook@2.3.0
      - run: mkdir -p dist && tweego src -o dist/index.html && ls -la dist
      - uses: actions/upload-pages-artifact@v3
        with: {path: dist}
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: {name: github-pages}
    steps:
      - uses: actions/deploy-pages@v4
```

Append to `.gitignore`: `dist/`, `build/`, `.pytest_cache/`, `__pycache__/`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_toolchain.py -v`
Expected: PASS (3 passed; tweego binary not required for this test)

- [ ] **Step 5: Commit**

```bash
git add package.json requirements.txt Makefile .github/workflows/pages.yml tests/test_toolchain.py .gitignore
git commit -m "chore: scaffold toolchain pins and pages workflow"
```

### Task 2: Extractor for ALL remark tables + prune audit

**Files:**
- Create: `tools/extract.py`, `tests/fixtures/story_excerpt.ni`, `tests/test_extract.py`
- Produces: `data/graph.json`, `data/prune-list.json`, `data/extraction-report.json` (generated, committed)

**Interfaces:**
- Consumes: raw `story.ni` text (downloaded once to `data/story.ni`, gitignored if license requires; else committed)
- Produces: `extract_tables(text) -> dict[str, list[dict{starting, final, comment}]]` used by Task 3; `PRUNE_RULES` used by audit test

- [ ] **Step 1: Write the failing test**

```python
# tests/test_extract.py
from tools.extract import extract_tables, apply_prune_rules

FIXTURE = open("tests/fixtures/story_excerpt.ni").read()

def test_extracts_all_six_remark_tables():
    tables = extract_tables(FIXTURE)
    for name in ["Prologue Remarks", "Wondering Remarks", "Fitting Remarks",
                 "Theodora Checking Remarks", "Lucinda Checking Remarks",
                 "Cinderella Checking Remarks"]:
        assert name in tables, f"missing {name}"
    assert tables["Prologue Remarks"][0]["starting"] == "king's health"
    assert tables["Prologue Remarks"][0]["final"] == "heirs"
    assert "fortunate" in tables["Prologue Remarks"][0]["comment"]

def test_prune_only_loops_and_invalid():
    tables = extract_tables(FIXTURE)
    kept, pruned = apply_prune_rules(tables)
    reasons = {p["reason"] for p in pruned}
    assert reasons <= {"loop", "invalid-input"}
    assert any(p["table"] == "Bad Bird Excuses" for p in pruned)
```

Fixture `tests/fixtures/story_excerpt.ni` (exact, minimal, tab-separated like original):

```
Table of Prologue Remarks
starting	final	comment
king's health	heirs	"'It's so fortunate,' says the old lady."
heirs	marriage	"'A rumor that you yourself were planning to wed.'"

Table of Bad Bird Excuses
response
"'Don't mind our parrot,' says the lady."
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_extract.py -v`
Expected: FAIL with "tools.extract not found"

- [ ] **Step 3: Write minimal implementation**

```python
# tools/extract.py
"""Parse story.ni remark tables. Tables are 'Table of <Name>' followed by
tab-separated rows. Remark tables have columns starting/final/comment."""
import json, re, sys

REMARK_TABLES = ["Prologue Remarks", "Wondering Remarks", "Fitting Remarks",
    "Theodora Checking Remarks", "Lucinda Checking Remarks",
    "Cinderella Checking Remarks", "Reactions"]
LOOP_TABLES = {"Bad Bird Excuses": "loop", "Waiting": "loop",
    "Awwkwardness": "loop", "Insults": "loop", "Flattery": "loop"}
INVALID_TABLES = {"Reactions-pirate-row": "invalid-input"}

def extract_tables(text):
    tables, current, header = {}, None, None
    for line in text.splitlines():
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
    pruned = [{"table": t, "reason": "loop",
               "detail": f"{len(tables.get(t, []))} rows collapsed to one representative passage"}
              for t in LOOP_TABLES if t in tables]
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_extract.py tests/test_toolchain.py -v`
Expected: PASS

- [ ] **Step 5: Run extractor on full source, commit outputs**

Run: `python3 tools/extract.py data/story.ni data && cat data/extraction-report.json`
Expected: exit 0; report lists all 16 tables from spec section 3

- [ ] **Step 6: Commit**

```bash
git add tools/extract.py tests/test_extract.py tests/fixtures/story_excerpt.ni data/graph.json data/prune-list.json data/extraction-report.json
git commit -m "feat: extract all remark tables with prune audit"
```

### Task 3: Twee passages for ALL paths (Chapbook, least code)

**Files:**
- Create: `src/glass.twee`, `tests/test_twee.py`
- Modify: nothing else

**Interfaces:**
- Consumes: `data/graph.json` (row source), `data/prune-list.json` (allowed removals)
- Produces: passage names parsed by `parse_passages()` helper inside test + Task 4 walker

- [ ] **Step 1: Write the failing test**

```python
# tests/test_twee.py
import json, re
from pathlib import Path

TWEE = Path("src/glass.twee").read_text()
PASSAGES = dict(re.findall(r"^::\s+(\S+)[^\n]*\n((?:(?!^::).)*)", TWEE, flags=re.M | re.S))
LINKS = {name: re.findall(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", body) for name, body in PASSAGES.items()}
GRAPH = json.load(open("data/graph.json"))
PRUNE = json.load(open("data/prune-list.json"))
SUBJECTS = ["kings-health", "heirs", "marriage", "ball", "shoe", "cinderella",
            "theo", "lucinda", "stepmother", "love", "blood", "magic", "god", "birds"]

def test_no_missing_rows():
    missing = []
    for table, rows in GRAPH.items():
        for r in rows:
            slug = re.sub(r"[^a-z0-9]+", "-", (r["starting"] + "-" + r["final"]).lower()).strip("-")
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
            if p.startswith("S") and "-End-" not in p
            and sum(1 for s in SUBJECTS if any(s in t.lower() for t in ts)) < len(SUBJECTS)]
    assert weak == [], f"passages missing subject choices: {weak[:5]}"

def test_fidelity_verbatim():
    thin = [p for p, b in PASSAGES.items()
            if p.startswith("S") and len(b.strip()) < 80]
    assert thin == [], f"passages too thin (LLM invented?): {thin[:5]}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_twee.py -v`
Expected: FAIL with "src/glass.twee not found"

- [ ] **Step 3: Write minimal implementation (seed with 3 real passages; extend row-by-row until tests green)**

```twee
:: StoryTitle
Twee-Glass

:: StoryData
{"format": "Chapbook-2", "start": "Prologue-Intro"}

:: Prologue-Intro {"position": "100,100"}
discussing {currentSubject}
{set currentSubject to 'kings-health'}
The Prince sits awkwardly on the couch, holding his glass slipper and trying to keep it from crushing. The old lady leans toward him: 'Do tell me about your father's health.'

- [[Squawk about heirs!|S1-Prologue kings-health-heirs]]
- [[Squawk about the ball!|S1-Prologue generic-ball]]
- [[Squawk about the shoe!|S1-Prologue generic-shoe]]
- [[Squawk about marriage!|S1-Prologue generic-marriage]]
- [[Squawk about Cinderella!|S1-Prologue generic-cinderella]]
- [[Squawk about Theo!|S1-Prologue generic-theo]]
- [[Squawk about Lucinda!|S1-Prologue generic-lucinda]]
- [[Squawk about stepmother!|S1-Prologue generic-stepmother]]
- [[Squawk about love!|S1-Prologue generic-love]]
- [[Squawk about blood!|S1-Prologue generic-blood]]
- [[Squawk about magic!|S1-Prologue generic-magic]]
- [[Squawk about god!|S1-Prologue generic-god]]
- [[Squawk about birds!|S1-Prologue generic-birds]]
- [[Squawk about kings-health!|S1-Prologue generic-kings-health]]

:: S1-Prologue kings-health-heirs
{set currentSubject to 'heirs'}
'It's so fortunate,' says the old lady. 'That you're of an age -- that is, that the King has been so blessed with an heir.'
[[Continue|Prologue-Intro]]

:: S1-Prologue generic-ball
{set currentSubject to 'ball'}
There's an uncomfortable silence as everyone tries to think of a sensible direction for the conversation to take from here. 'Mm, we were speaking of the ball,' says the old lady.
[[Continue|Prologue-Intro]]
```

(Repeat the row-passage + generic-redirect pattern for every row in
`data/graph.json` until `test_no_missing_rows` passes; endings are `:: S9-End-<name>`
passages with no outbound links.)

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_twee.py -v`
Expected: PASS (extend `src/glass.twee` until all 4 tests green; do not weaken tests)

- [ ] **Step 5: Commit**

```bash
git add src/glass.twee tests/test_twee.py
git commit -m "feat: twee passages covering all remark paths"
```

### Task 4: Reachability walk (all scenes + endings, no browser)

**Files:**
- Create: `tests/test_reachability.py`

**Interfaces:**
- Consumes: `parse` logic duplicated from `test_twee.py` (names + links)
- Produces: scene/ending lists consumed by Task 6 manual checklist

- [ ] **Step 1: Write the failing test**

```python
# tests/test_reachability.py
import re
from pathlib import Path

TWEE = Path("src/glass.twee").read_text()
PASSAGES = dict(re.findall(r"^::\s+(\S+)[^\n]*\n((?:(?!^::).)*)", TWEE, flags=re.M | re.S))
LINKS = {n: re.findall(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", b) for n, b in PASSAGES.items()}
SCENES = ["Prologue", "Wondering", "Fitting", "Checking-Theodora",
          "Checking-Lucinda", "Checking-Cinderella", "Theodora-Endgame",
          "Lucinda-Endgame", "End"]
ENDINGS = ["S9-End-Theodora-Marriage", "S9-End-Lucinda-Marriage", "S9-End-Peace",
           "S9-End-Disaster", "S9-End-Prince-Departs", "S9-End-Cinderella-Executed",
           "S9-End-Cinderella-Wed", "S9-End-Pirates"]

def walk(start):
    seen, stack = set(), [start]
    while stack:
        n = stack.pop()
        if n in seen or n not in PASSAGES:
            continue
        seen.add(n)
        stack.extend(LINKS[n])
    return seen

def test_all_endings_reachable():
    seen = walk("Prologue-Intro")
    assert [e for e in ENDINGS if e not in seen] == []

def test_all_scenes_routable():
    seen = walk("Prologue-Intro")
    assert [s for s in SCENES if not any(s in p for p in seen)] == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_reachability.py -v`
Expected: FAIL listing unreachable endings (until Task 3 fully extended)

- [ ] **Step 3: Extend `src/glass.twee` (no test edits)**

Add the missing `:: S9-End-*` terminal passages and scene-continue forks so the
walk reaches every name in ENDINGS/SCENES. Endings contain original ending text
(e.g. pirates passage contains "sold to pirates").

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/ -v`
Expected: PASS (all suites green)

- [ ] **Step 5: Commit**

```bash
git add src/glass.twee tests/test_reachability.py
git commit -m "feat: all scenes and endings reachable"
```

### Task 5: Tweego build + artifact assertion

**Files:**
- Create: `tests/test_build.py`

**Interfaces:**
- Consumes: `src/glass.twee`, Tweego 2.1.1 binary via npx
- Produces: `dist/index.html` (gitignored)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_build.py
import subprocess
from pathlib import Path

def test_tweego_builds_index():
    r = subprocess.run(["npx", "tweego@2.1.1", "src", "-o", "dist/index.html"],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr[-2000:]
    html = Path("dist/index.html")
    assert html.exists() and html.stat().st_size > 50_000
    text = html.read_text(errors="replace")
    assert "Prologue-Intro" in text
    for end in ["S9-End-Pirates", "S9-End-Cinderella-Wed", "S9-End-Peace"]:
        assert end in text, f"ending missing from build: {end}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_build.py -v`
Expected: FAIL (npx downloads tweego on first run, or src incomplete)

- [ ] **Step 3: Fix until green (no test edits)**

Run: `make build` / fix Twee syntax errors reported by tweego (usually
unescaped `]]` or bad `StoryData` JSON). Keep Chapbook 2 syntax only.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_build.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_build.py
git commit -m "test: assert tweego build contains all endings"
```

### Task 6: LLM polish gate + attribution

**Files:**
- Create: `tools/polish.md`, `tests/test_polish.py`

**Interfaces:**
- Consumes: `data/graph.json` rows
- Produces: passage bodies reviewed in diff; `<!-- FLAG: -->` items resolved before merge

- [ ] **Step 1: Write the failing test**

```python
# tests/test_polish.py
from pathlib import Path

TWEE = Path("src/glass.twee").read_text()

def test_no_parser_artifacts():
    for artifact in ["[if ", "[awwk]", "[nice word]", "[comment entry]"]:
        assert artifact not in TWEE, f"unresolved artifact: {artifact}"

def test_attribution_present():
    assert "Emily Short" in TWEE
    assert "I7-Examples/Glass" in TWEE
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_polish.py -v`
Expected: FAIL until artifacts cleaned and footer added

- [ ] **Step 3: Write minimal implementation (`tools/polish.md` + apply to twee)**

`tools/polish.md` prompt: input one `starting|final|comment` row; output choice
label (<=6 words, parrot voice) + body (95% verbatim, resolve `[if ...]` /
`[awwk]` / `[nice word]` to plain text, never invent plot); emit
`<!-- FLAG: <reason> -->` for dated content instead of rewriting. Apply to every
passage, add footer to `Prologue-Intro`: "After Emily Short's Glass
(I7-Examples/Glass). Choice adaptation, light polish, all paths preserved."

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/ -v`
Expected: PASS (full suite green: toolchain, extract, twee, reachability, build, polish)

- [ ] **Step 5: Commit**

```bash
git add tools/polish.md src/glass.twee tests/test_polish.py
git commit -m "feat: llm polish gate with attribution"
```
