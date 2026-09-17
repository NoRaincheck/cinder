# SRD — Cinder (durable)

**Status:** durable — default branch alone is sufficient to operate and recover the system.
**Scope:** Choice-based Twine ports of Emily Short's Inform 7 games *Glass*, *Bronze*, and *Indigo* (curated tower spine).
Player steers drawing-room talk in Glass; free-text `mention [subject]` becomes
clickable subject choices. Bronze is a curated castle spine.
**Toolchain:** Chapbook 2.3.0 via Tweego 2.1.1 → static `dist/glass.html`,
`dist/bronze.html`, `dist/indigo.html`, landing `dist/index.html` (GitHub Pages). No custom JS.
**Date:** 2026-09-16

> **Durability contract** (per `ref/docs/agentic-engineering.md` §6): this
> document states invariants directly in domain language, uses stable paths,
> and provides role-based runbooks. Planning documents (`docs/superpowers/…`)
> are ephemeral — they may point here, never the reverse — and are deleted
> post-merge. Nothing here references a branch, a PR, or a planning tree.

## Stable paths

| Role | Path |
|---|---|
| Glass source | `src/glass/glass.twee` (30 story passages + `StoryTitle`, `StoryData`) |
| Bronze source | `src/bronze/bronze.twee` (28 story passages + `StoryTitle`, `StoryData`) |
| Indigo source | `src/indigo/indigo.twee` (20 story passages + `StoryTitle`, `StoryData`) |
| Canonical Inform sources | `ref/source/glass.ni`, `ref/source/bronze.ni` (committed renames of upstream `story.ni`; see `ref/source/README.md`) |
| TADS source | `ref/source/indigo.t3` (compiled image; manual transcription) |
| Extraction outputs | `data/graph.json`, `data/prune-list.json`, `data/extraction-report.json` (Glass); `data/bronze-graph.json`, `data/bronze-prune-list.json`, `data/bronze-extraction-report.json` (Bronze); `data/indigo-graph.json`, `data/indigo-prune-list.json`, `data/indigo-extraction-report.json` (Indigo) |
| Build artifacts (gitignored) | `dist/glass.html`, `dist/bronze.html`, `dist/indigo.html`, `dist/index.html` (landing) |
| Tooling | `tools/extract.py`, `tools/curate3.py`, `tools/build-landing.py`, `tools/patch-chapbook.js`, `tools/setup-tweego.sh`, `tools/polish.md` |
| Tests | `tests/` (`just test` runs the full suite; Pages deploys only on green) |
| Delivery | `justfile`, `.github/workflows/pages.yml` |

## Goal

Port *Glass* (and a curated *Bronze*) to choice-based HTML while preserving
every narrative path. The only removals allowed are loop rows
(repeat-of-current-subject scolds, one-shot-blanked rows, filler variation
tables) and invalid-input handlers (unknown-topic fallback, directed-speech
errors, scenery-action stubs). Everything else ships. Polish is light: ~95%
verbatim dialogue, parser artifacts resolved, dated content flagged for human
review, never silently rewritten.

## Design decisions (invariants)

### D2 — Extraction is verbatim ground truth

`tools/extract.py` parses the 7 Glass remark tables (Prologue, Wondering,
Fitting, Theodora/Lucinda/Cinderella Checking, Reactions) into
`data/graph.json` verbatim. Loop tables (`Bad Bird Excuses`, `Waiting`,
`Awwkwardness`, `Insults`, `Flattery`) and one-shot flavor tables
(`Lucinda Checks`, `Theodora Checks`) are excluded from the graph but counted
in `data/extraction-report.json` — those counts are NOT missing content.
Pruned rows go to `data/prune-list.json` with a `reason` (`loop` / `user-cut` /
`curated-3`). Bronze: `scan_bronze()` lists rooms + tables into
`data/bronze-graph.json`, with cuts audited in
`data/bronze-prune-list.json`. **Invariant:** no remark row is silently
dropped — every row is either a passage or a prune entry (enforced by
`test_no_missing_rows` and the Bronze graph tests).

### D3 — Curated ≤3-choice spine

Passages offer **≤3 story choices per screen**; navigation links (Back /
Continue / Press) don't count toward the 3. `tools/curate3.py` rewrites hub
blocks to ≤3 `Steer toward…` story links plus nav, deletes the `S-Hub-*`
fan-out passages, and appends `Back-to-Hub` to every kept row. Bodies stay
verbatim. **Rationale:** a dense hub (S1 exposed 71 links) is unplayable; the
spine keeps all endings reachable within a readable choice surface.
**Invariant:** `tools/curate3.py --story {glass,bronze}` is the only
bulk-rewriter; story bodies are never hand-trimmed to fit the budget.

### D4 — One-shot links (anti-loop)

Each row passage (excluding hubs/endings) opens with a vars section setting
`seen_<slug>: true`, then `--`, then the body. Every link to a row is guarded
by `[unless seen_*]` so visited choices vanish — mirroring the original
"blank the row after use." **Never** guard hub, ending, intro, or funnel
links. Flags are snake_case; additive only; never nested. Each story's start
passage must initialize every `seen_*` read anywhere in that story (Chapbook
evaluates `[if seen_*]` as raw JS and throws on undefined vars).

### D6 — Scene gating (forward-only progression)

Glass arc: Prologue → Wondering → Fitting → Checking (T/L/C) → Endgames.
Gates live behind key-row flags (S1→S2 behind
`seen_s1_prologue_blank_shoe_1`, S2→S3 behind
`seen_s2_wondering_blank_ball_1`, S3→Checking behind
`seen_s3_fitting_blank_theo_1`). Each ending is homed to exactly one scene.
Checking→endgame funnels stay unconditional. Bronze: the three
`Bronze-Choice-*` passages link only to their matching ending (forward-only
gating). **Polarity:** appear-gates use `[if seen_*]` (Continue links),
vanish-gates use `[unless seen_*]` (row links) — inverted polarity strands
players and is test-enforced (`test_clickability.py`).

### D7 — Bird layer removed (de-birding)

All parrot/polly/feathers framing and the birds topic were cut: no `squawk` /
`awwk` wording, no `The birds` links, no `S-Hub-birds`, none of the 9
birds-topic passages remain (3 flavor cuts + 6 topic rows, all `user-cut`).
5 remaining "bird" words live in story-dialogue lines (see Open items); the
wing chair is kept. `data/graph.json` still mirrors original text verbatim as
the extraction source. **Open question:** whether to also drop the 5
story-dialogue "bird" lines.

### D8 — Navigation rendering

All non-story navigation renders as a bare `>` (no ending/return-to info in
the label). Scope terminators (`[if 2 + 2 === 4]`) terminate any open
`[unless]`/`[if]` before trailing nav, since Chapbook modifiers leak onto all
following text.

### D9 — Toolchain & delivery

`justfile` recipes: `setup` (pytest pins + Tweego/Chapbook fetch),
`build-glass` / `build-bronze` / `build-landing` / `build` (all three, then
`node tools/patch-chapbook.js <artifact>` per story),
`test` (pytest), `extract [glass|bronze|all]`, `preview` (serve `dist/`),
`clean`, `fmt`. `.github/workflows/pages.yml` builds + deploys `main` to
Pages with a pytest gate. Canonical Inform sources are the committed
`ref/source/glass.ni` + `ref/source/bronze.ni`; `just extract` restores either
from its snapshot URL only if missing, then parses it straight into `data/`.

### D10 — Prologue magic-lore branches with forward callbacks (Glass)

`Start` offers three prologue topics (Marriage / Ball / Shoe), each fanning to
two lore sub-passages (`Prologue-Marriage-Enchantment`, `-Law`,
`Prologue-Ball-Beauty`, `-Memory`, `Prologue-Shoe-Nature`, `-Truth`). Each
sub-passage opens with a vars section setting its `prologue*` flag, then
`--`, then the body. `Wondering-Marriage` / `-Ball` / `-Shoe` close with
`[if prologueX]` conditional paragraphs, each terminated by `[continue]`, so
earlier lore echoes forward without gating progression. **Invariants:**
`Start` must initialize every `prologue*` flag read anywhere (Chapbook
evaluates `[if …]` as raw JS and throws on undefined vars); flags are
camelCase, additive only, never nested; every `[if prologue*]` block is
closed by `[continue]` before the next block or trailing nav
(`tools/patch-chapbook.js` makes `[continue]` reset `conditionEval` — see
D11). Enforced by `tests/test_polish.py` and `tests/test_reachability.py`.

### D11 — Chapbook `[continue]` conditionEval patch (build-time)

Chapbook 2.3.0's `[continue]` modifier has an empty `process()`, so
`conditionEval` set by a preceding `[if]` bleeds into following blocks in the
same passage and blanks text after a false conditional. `just build` runs
`node tools/patch-chapbook.js <artifact>` per story artifact after Tweego: it
rewrites the single `process(){}}` occurrence in the artifact to
`process(n,c){c.state.conditionEval=void 0}}` (and repairs the earlier broken
single-arg `process(c)` form if present). **Invariant:** never hand-edit
`dist/`; rerun `just build` to re-apply. Runbook: patch prints
`Patched 1 occurrence(s) …`; `No patches needed` means the engine string
moved and the script needs updating. `node tools/patch-chapbook.js --help`
prints usage; default target is the legacy `dist/index.html`.

### D12 — Endings grounded to canonical Glass outcomes

Endings are the canonical `glass.ni` outcomes: `End-Cinderella-Wed` (shoe
destroyed/left untested → wed), `End-Cinderella-Executed` (magic exposed →
executed; reachable via `Cinderella-Tries → [[> |End-Cinderella-Executed]]`),
`End-Lucinda-Marriage` (via `[[Mention the blood|End-Prince-Departs]]`
branch wording; blood cue added to `Lucinda-Tries`), `End-Prince-Departs`,
plus terminal `Theodora-Marriage` (5 terminal outcomes total; no
`End-Pirates`, no standalone `End-Peace` / `End-Disaster` — their text folded
into `Check-Cinderella` summoning and the `Cinderella-Tries` → Executed
funnel). **Invariant:** every non-meta passage is reachable from `Start`
(`tests/test_reachability.py`, `ORPHANS = {"vars"}` — `vars` is a Chapbook
meta-section, not a passage); `tests/test_build.py` asserts
`End-Cinderella-Wed`, `End-Lucinda-Marriage`, `End-Cinderella-Executed`
present in the built `dist/glass.html`.

### D13 — Multi-story site (Glass + Bronze + Indigo)

Split-src, multi-compile, static landing. Each story keeps its own
`StoryTitle` / `StoryData` (own IFID, own start passage: `Start` for Glass,
`Bronze-Start` for Bronze, `Indigo-Start` for Indigo); no shared passages; all Bronze passages are
`Bronze-`-prefixed (28 story passages, 3 endings: `End-Bronze-Leave`,
`End-Bronze-Stay`, `End-Bronze-Beast`); all Indigo passages are
`Indigo-`-prefixed (20 story passages, 2 endings: `End-Indigo-Escape`,
`End-Indigo-Spoiled`). `tools/build-landing.py` (stdlib
only) renders story cards into `dist/index.html` and fails if any story
artifact is missing (no dangling Play links). **Invariants:** Glass IFID
`C67460F1-5CAD-42EC-AF08-E1A7249DBCE8` never changes; Bronze IFID is fixed at
creation; Indigo IFID is fixed at creation; `dist/index.html` is the landing, never a game (old `#passage`
deep links to the single-story index are retired — accepted, noted in
`README.md`); `tests/test_build.py` asserts all three artifacts >50KB with their
titles/endings plus landing links.

## Runbooks

### Operator — build, verify, ship

1. `just setup` once (fetches Tweego 2.1.1 + Chapbook 2.3.0 into `build/`).
2. `just build` (compiles `src/glass` → `dist/glass.html`,
   `src/bronze` → `dist/bronze.html`, patches each, generates landing).
3. `just test` — full pytest suite is the Pages gate; do not ship red.
4. `just preview` — serve `dist/` locally (landing at `/`, stories at
   `/glass.html`, `/bronze.html`).
5. Push `main` — `.github/workflows/pages.yml` rebuilds, re-tests, deploys.

### Author — add or edit story content

1. Dialogue stays ~95% verbatim from `ref/source/*.ni`; fix only parser
   artifacts per `tools/polish.md`; dated content gets
   `<!-- FLAG: <reason> -->`, never a silent rewrite.
2. New passages go in the owning story dir with the owning prefix
   (`Bronze-` for Bronze); links end with two trailing spaces (`just fmt`
   enforces the Chapbook link rule).
3. One-shot rows: leading vars `seen_*: true` + `[unless seen_*]` links;
   never guard hubs, endings, intros, or funnels. New `seen_*`/`prologue*`
   flags must be initialized in the story start passage.
4. Record cuts in the owning `data/*prune-list.json` with a `reason`;
   re-run `just extract <story>` to confirm no row is silently dropped.

### Agent — extract, curate, verify loop

1. `just extract [glass|bronze|all]` — restores missing `ref/source/*.ni`
   from snapshot URLs, re-parses into `data/`; unknown Bronze table shapes
   warn to stderr and skip with exit 0 so Glass never breaks.
2. `tools/curate3.py --story {glass,bronze}` is the only bulk rewriter.
3. `just test` after every change; reachability (every ending from story
   start), link integrity (no dead links, hubs never empty), oneshot guards,
   polish, and build-contains-endings must all hold.
4. Never commit `dist/`; never hand-edit build output (re-apply via
   `just build`); never reference `docs/superpowers/…` planning paths from
   durable docs or shipped code.

## Key numbers

| | Glass | Bronze | Indigo |
|---|---|---|---|
| Story passages | 30 + 2 meta (`StoryTitle`, `StoryData`) in `src/glass/glass.twee` | 28 + 2 meta in `src/bronze/bronze.twee` | 20 + 2 meta in `src/indigo/indigo.twee` |
| Prologue lore leaves | 6 (`Prologue-*-Enchantment/Law/Beauty/Memory/Nature/Truth`) | n/a | n/a |
| Endings | 5 (4 `End-*` + terminal `Theodora-Marriage`; D12) | 3 (`End-Bronze-Leave/Stay/Beast`) | 2 (`End-Indigo-Escape/Spoiled`) |
| Build artifact | `dist/glass.html` | `dist/bronze.html` | `dist/indigo.html` |

## Open items

- D7 follow-up: decide on the 5 remaining story-dialogue "bird" lines.
- D10 gap (bug): `Start` initializes 5 flags but `Wondering-Ball` reads 7 —
  `prologueBeauty` / `prologueMemory` are set by their lore leaves but never
  initialized in `Start`; add them (`prologueBeauty: false`,
  `prologueMemory: false`) or Chapbook throws on the unvisited path.
  `skipPrologue` is initialized but never read — either wire it or drop it.
- Two passages in `glass.ni` have truncated dialogue (magic-birds,
  marriage-birds) from a known extractor bug; full text is restorable
  independently.
- `dist/` is gitignored; only build artifacts deploy.
