# Multi-Story Site: Glass + Bronze — Design

Date: 2026-09-16
Status: draft for review (no code changes yet)
Decisions already taken: Bronze scope = curated spine; selector shape = multi-page builds.
Assumptions pending confirmation: static landing OK; Bronze budget ~25–30 passages + 3 endings.

## 1. Goal

Add Emily Short's **Bronze** as a second playable story alongside **Glass**.
Upstream: `https://github.com/I7-Examples/Bronze/blob/main/Bronze.inform/Source/story.ni`
committed locally as `ref/source/bronze.ni`. The built site becomes a selector:
landing `dist/index.html` → `dist/glass.html` + `dist/bronze.html`.

Non-goals: full Bronze puzzle-geography parity (hint system, all 40+ rooms);
rewriting Glass passages; changing the Chapbook/Tweego toolchain pins.

## 2. Architecture

Split-src, multi-compile, static landing (Approach 1):

- `src/glass/glass.twee` (moved verbatim from `src/glass.twee`)
- `src/bronze/bronze.twee` (new, curated spine)
- `dist/glass.html`, `dist/bronze.html` via two Tweego invocations
- `dist/index.html` static landing generated from story metadata (no Chapbook JS)

Each story keeps its own `StoryTitle` / `StoryData` (own IFID, own start
passage). No shared passages. Pages workflow uploads `dist/` unchanged.

Rejected: single-src tag filtering (Tweego has no tag filter; `StoryTitle` /
`StoryData` / `Start` collisions); per-story monorepo packages (overkill).

## 3. Components

1. **Source copies** — `ref/source/glass.ni` untouched; new `ref/source/bronze.ni`
   + `ref/source/README.md` update (both upstream URLs, rename note).
2. **Bronze Twee** — `src/bronze/bronze.twee`, all passages `Bronze-`-prefixed
   (`Bronze-Start`, `Bronze-Entrance-Hall`, …), 2 meta passages
   (`StoryTitle`, `StoryData`). Bronze IFID generated fresh (uuidgen) at
   implementation time; Glass IFID unchanged.
3. **Extraction** — `tools/extract.py` keeps Glass path byte-identical; adds
   Bronze scanner (rooms, history/hint tables) → `data/bronze-graph.json`,
   `data/bronze-prune-list.json`, `data/bronze-extraction-report.json`.
   `tools/curate3.py` gains `--story {glass,bronze}`.
4. **Landing** — `tools/build-landing.py` (new, stdlib only) renders story cards
   (title, headline, description, Play link) into `dist/index.html`.
5. **Build** — `justfile`: `build-glass`, `build-bronze`, `build-landing`,
   `build` = all three; `preview` serves `dist/`; `patch-chapbook.js` must gain
   a target-file arg (it currently hardcodes `dist/index.html`) and run once
   per story artifact.
6. **Tests** — existing Glass tests parameterized by story; new
   `tests/test_landing.py`; `test_build.py` asserts both artifacts + links.

## 4. Data flow

1. `just extract bronze` parses `ref/source/bronze.ni` → bronze data files.
2. Curation (assisted, manual) produces `src/bronze/bronze.twee` reusing Glass
   semantics: leading vars-section `seen_*` flags, `[unless seen_*]` one-shot
   guards, struck-through visited hub links, forward-only scene gating.
3. `just build` compiles each story dir, patches Chapbook, generates landing.
4. `just test` verifies links, reachability, oneshot behavior, landing content.

Bronze starter spine (~25–30 passages, 3 endings): Drawbridge → Entrance Hall
→ Central Courtyard → Scarlet Gallery → Treasure Room → Maze Room / Bear
Corridor → Beast encounter → curated endings. Dialogue verbatim except parser
artifacts; cuts audited in `bronze-prune-list.json` per `tools/polish.md`.

## 5. Error handling

- `extract` with missing `ref/source/*.ni` restores from per-story snapshot URL,
   else fails loudly (no silent empty graph).
- Bronze scanner on unrecognized table shape warns + skips (exit 0) so Glass
   extraction never breaks.
- `build-landing` fails if either story artifact is missing (no dangling Play
   links); Tweego failure aborts before landing generation.
- Old `#passage` deep links to single-story `index.html` change meaning
   (now landing) — accepted, noted in README.

## 6. Testing

- Keep all 18 existing Glass assertions green (`data/graph.json` contract
   unchanged).
- New/parameterized: per-story link integrity (no dead links, hubs never
   empty), reachability (every ending from story start), oneshot guards,
   polish (verbatim except flagged artifacts).
- `test_build.py`: `glass.html` + `bronze.html` each >50KB, contain their
   `StoryTitle` + endings; landing contains both cards + Play links.
- `just test` is the Pages gate (unchanged workflow).

## 7. Migration

- One-time move `src/glass.twee` → `src/glass/glass.twee` (content identical).
- `dist/index.html` changes from game to landing (breaking old fragment URLs).
- README Layout/recipes table updated (`extract glass|bronze|all`, new build
   recipes, new paths).

## 8. Open questions for reviewer

1. Static landing acceptable, or Chapbook landing?
2. Bronze budget: ~30 passages / 3 endings, or smaller 10–15 MVP first?
3. Which Bronze puzzles make the starter cut (helmet / cage / maze / Beast)?
