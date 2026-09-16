# SRD — Twee-Glass

**Project:** Choice-based Twine port of Emily Short's Inform 7 game *Glass*
(I7-Examples/Glass). Player is the parrot; free-text `mention [subject]`
becomes clickable subject choices.
**Branch:** `prologue-magic-lore` (against `main`)
**Format:** Chapbook 2.3.0 via Tweego 2.1.1 → static `dist/index.html` (GitHub Pages). No custom JS.
**Date:** 2026-09-16

> **Read this first (state of the branch).** The design/decision artifacts on
> this branch (specs, `polish.md`, `curate3.py`, the test suite) describe a
> rich architecture: a curated ≤3-choice spine where each row passage sets a
> `seen_*` flag, visited rows vanish via `[unless seen_*]`, visited hubs render
> struck-through, and scenes unlock behind `[if seen_*]` gates. The committed
> `src/glass.twee`, however, is a **simpler hand-authored linear spine** that
> does **not** contain any of that machinery (no `Prologue-Intro`, no `S\d` row
> passages, no `S1-Prologue-Hub`… scene hubs, no `[if/unless seen_*]` guards).
> It **does** contain the D10–D12 machinery added on this branch: a `Start`
> vars section, six `Prologue-*-*` lore sub-passages setting `prologue*`
> flags, and `[if prologue*]` / `[continue]` callbacks in `Wondering-*`.
> The test suite was adapted so that **all tests pass** — reachability allows
> the `vars` meta-section as an orphan, polish allows Chapbook conditionals
> (`[if camelCase]`, `[if !var]`) plus the always-true scope terminator.
> Treat the SRD below as the *recorded design decisions*; the "Implementation
> status" section records where the committed code actually stands.

## Goal

Port *Glass* to choice-based HTML while preserving every narrative path. The
only removals allowed are loop rows (repeat-of-current-subject scolds,
one-shot-blanked rows, filler variation tables) and invalid-input handlers
(unknown-topic fallback, directed-speech errors, scenery-action stubs).
Everything else ships. Polish is light: ~95% verbatim dialogue, parser
artifacts resolved, dated content flagged for human review, never silently
rewritten.

## Design decisions (recorded on the branch)

### D2 — Extraction is verbatim ground truth
`tools/extract.py` parses the 7 remark tables (Prologue, Wondering, Fitting,
Theodora/Lucinda/Cinderella Checking, Reactions) into `data/graph.json`
verbatim. Loop tables (`Bad Bird Excuses`, `Waiting`, `Awwkwardness`,
`Insults`, `Flattery`) and one-shot flavor tables (`Lucinda Checks`,
`Theodora Checks`) are excluded from the graph but counted in
`data/extraction-report.json` — those counts are NOT missing content. Pruned
rows go to `data/prune-list.json` with a `reason` (`loop` / `user-cut` /
`curated-3`). **Invariant:** no remark row is silently dropped — every row is
either a passage or a prune entry (enforced by `test_no_missing_rows`).

### D3 — Curated 3-choice spine (overrides the original all-paths design)
The 2026-09-14 design specified full connectivity (every passage links every
subject). On 2026-09-15 this became a curated spine: **≤3 story choices per
screen**; navigation links don't count toward the 3. `tools/curate3.py`
rewrites hub blocks to ≤3 `Steer toward…` story links plus Back/Continue/Press
nav, deletes all 13 `S-Hub-*` fan-out passages (~1,638 quad links), and appends
`Back-to-Hub` to every kept row. Bodies stay verbatim. **Rationale:** a dense
hub (S1 exposed 71 links) is unplayable; the spine keeps all endings reachable
within a readable choice surface.

### D4 — One-shot links (anti-loop)
Each row passage (`S<digit>…`, excluding hubs/endings) opens with a vars section
setting `seen_<slug>: true`, then `--`, then the body. Every link to a row is
guarded by `[unless seen_*]` so visited choices vanish — mirroring the original
"blank the row after use." **Never** guard hub, ending, intro, or funnel links.
Flags are snake_case; additive only; never nested. The start passage must
initialize every `seen_*` used anywhere (Chapbook evaluates `[if seen_*]` as
raw JS and throws on undefined vars).

### D6 — Scene gating (forward-only progression)
Arc: Prologue → Wondering → Fitting → Checking(T/L/C) → Endgames. Gates live
behind key-row flags: S1→S2 behind `seen_s1_prologue_blank_shoe_1`,
S2→S3 behind `seen_s2_wondering_blank_ball_1`, S3→Checking behind
`seen_s3_fitting_blank_theo_1`. Each ending is homed to exactly one scene
(S1 Pirates / S2 Prince-Departs / S3 Disaster / S6 Peace+Executed+Wed /
S7 Theodora-Marriage / S8 Lucinda-Marriage). Checking→endgame funnels stay
unconditional. **Polarity:** appear-gates use `[if seen_*]` (Continue links),
vanish-gates use `[unless seen_*]` (row links) — inverted polarity strands
players and is test-enforced (`test_clickability.py`).

### D7 — Bird layer removed (de-birding)
All parrot/polly/feathers framing and the birds topic were cut: no `squawk` /
`awwk` wording, no `The birds` links, no `S-Hub-birds`, none of the 9
birds-topic passages remain (3 flavor cuts + 6 topic rows, all `user-cut`).
5 remaining "bird" words live in story-dialogue lines (see
`../docs/bird-paths-review.md`); the wing chair is kept. `data/graph.json`
still mirrors original text verbatim as the extraction source. **Open
question:** whether to also drop the 5 story-dialogue "bird" lines.

### D8 — Navigation rendering
All non-story navigation renders as a bare `>` (no ending/return-to info in
the label). Scope terminators (`[if 2 + 2 === 4]`) terminate any open
`[unless]`/`[if]` before trailing nav, since Chapbook modifiers leak onto all
following text.

### D9 — Toolchain & delivery
`justfile` recipes: `setup` (pytest pins + Tweego/Chapbook fetch), `build`
(Chapbook → `dist/index.html`, then `node tools/patch-chapbook.js`), `test`
(pytest), `extract`, `preview`, `clean`, `fmt`.
`.github/workflows/pages.yml` builds + deploys `main` to Pages with a pytest
gate. Canonical Inform source is the committed `ref/source/glass.ni`
(renamed from upstream `story.ni`); `just extract` restores it from the
snapshot only if missing, then parses it straight into `data/`.

### D10 — Prologue magic-lore branches with forward callbacks
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
D11). Enforced by `tests/test_polish.py` (allows only the always-true scope
terminator, `seen_*` gates, `[if camelCase]`, `[if !var]`) and
`tests/test_reachability.py`.

### D11 — Chapbook `[continue]` conditionEval patch (build-time)
Chapbook 2.3.0's `[continue]` modifier has an empty `process()`, so
`conditionEval` set by a preceding `[if]` bleeds into following blocks in the
same passage and blanks text after a false conditional. `just build` runs
`node tools/patch-chapbook.js` after Tweego: it rewrites the single
`process(){}}` occurrence in `dist/index.html` to
`process(n,c){c.state.conditionEval=void 0}}` (and repairs the earlier broken
single-arg `process(c)` form if present). **Invariant:** never hand-edit
`dist/`; rerun `just build` to re-apply. Runbook: `just build` → patch prints
`Patched 1 occurrence(s)`; `No patches needed` means the engine string moved
and the script needs updating.

### D12 — Endings grounded to canonical Glass outcomes
Endings are the canonical `glass.ni` outcomes, not the D6 `S9-End-*` homes:
`End-Cinderella-Wed` (shoe destroyed/left untested → wed),
`End-Cinderella-Executed` (magic exposed → executed; reachable via
`Cinderella-Tries → [[> |End-Cinderella-Executed]]`),
`End-Lucinda-Marriage` (via `[[Mention the blood|End-Prince-Departs]]`
branch wording; blood cue added to `Lucinda-Tries`),
`End-Prince-Departs`, plus terminal `Theodora-Marriage`. Removed:
`End-Peace` and `End-Disaster` as standalone passages (their text folded into
`Check-Cinderella` summoning and the `Cinderella-Tries` → Executed funnel).
**Invariant:** every non-meta passage is reachable from `Start`
(`tests/test_reachability.py`, `ORPHANS = {"vars"}` — `vars` is a Chapbook
meta-section, not a passage); `tests/test_build.py` asserts
`End-Cinderella-Wed`, `End-Lucinda-Marriage`, `End-Cinderella-Executed`
present in the built HTML.

## Implementation status (committed code vs. the decisions above)

The committed `src/glass.twee` is a **hand-authored linear spine with prologue
lore callbacks** (`Start` → Prologue topics → Prologue lore leaves →
Wondering → Fitting → Checking → endings) that bypasses the D3–D4, D6
machinery but implements D10–D12:

- No `Prologue-Intro`, no `S\d` row passages, no `S1-Prologue-Hub`… scene hubs,
  no `[if/unless seen_*]` guards, no struck-through hub quads, no `S-Hub-*`
  passages (so D3/D4/D6 are **not implemented**).
- Present: `Start` vars section (`skipPrologue`, `prologueEnchantment`,
  `prologueLaw`, `prologueNature`, `prologueTruth`), six `Prologue-*-*` lore
  passages, `[if prologue*]` / `[continue]` callbacks in all three
  `Wondering-*` passages, and the D12 ending set (4 `End-*` passages +
  terminal `Theodora-Marriage` = **5** terminal outcomes; no `End-Pirates`,
  no standalone `End-Peace` / `End-Disaster`).
- The test suite passes — reachability asserts full connectivity from `Start`
  (`ORPHANS = {"vars"}`), build asserts the three canonical endings in
  `dist/index.html`, polish asserts no unresolved parser artifacts.

## Key numbers

| | Design contract | Committed file |
|---|---|---|
| Passages | 136 (all-paths) → curated spine | 30 story + 2 meta (`StoryTitle`, `StoryData`) |
| Story rows | 15 (`curate3.py` KEEP) | 0 (`S\d` rows) |
| Prologue lore leaves | — (D10) | 6 (`Prologue-*-Enchantment/Law/Beauty/Memory/Nature/Truth`) |
| Scene hubs | S1–S8 | none (flat scene names) |
| Endings | 8 (`S9-End-*` + 2 marriage hubs) | 5 (4 `End-*` + Theodora-Marriage; D12) |
| `S-Hub-*` | deleted | n/a (absent) |

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
- `ref/source/glass.ni` (committed rename of upstream `story.ni`) is the
  extraction source; `dist/` is gitignored; only build artifacts deploy.