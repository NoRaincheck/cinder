# 3-Choice Curated Path Design

**Date:** 2026-09-15
**Status:** draft for review (architectural path, brainstorming skill)
**Decisions locked from Q&A:** 3 story + navigation; curated critical path; `vendor/glass`; tests may be rewritten.

## 1. Goal

Reduce every screen to at most 3 story choices while keeping all 8 endings reachable from `Prologue-Intro`. Add upstream `https://github.com/I7-Examples/Glass` as a git submodule so `story.ni` is pinned, not curl-fetched.

Current state: `src/glass.twee` 8037 lines / 136 passages. S1-Prologue-Hub exposes 71 links (56 rows + 13 `S-Hub-*` + Continue + ending). Tests enforce the dense design (`test_twee:all-subjects`, `test_oneshot:104 rows`, `test_hubstrike:1638 quads`). All must be rewritten by design.

## 2. Navigation rule

Per passage: max 3 story links (`Steer toward…`) plus navigation-only links, which do NOT count toward the 3:

- `Continue to …` (scene gating, `[if seen_*]` guarded)
- `Back to … Hub` / `Take up … talk` (return, unconditional)
- `Press on toward S9-End-*` (ending, unconditional)

Counting rule for tests: `story_links = all [[..|..]] − navigation labels (Continue to|Back to|Take up|Press on toward)`. Assert `story_links <= 3` for every passage starting with `S` or `Prologue-Intro`.

`S-Hub-*` subject hubs (13 passages, 1638 quad links) are deleted entirely. They exist only to fan out 13 choices and cannot survive a 3-choice rule. Subject labels survive only as `Steer toward X` story links pointing directly at row passages.

## 3. Submodule / source

- `git submodule add https://github.com/I7-Examples/Glass.git vendor/glass` (track `main`, pin commit in `.gitmodules`).
- `just extract`: source priority `vendor/glass/Glass.inform/Source/story.ni` → fallback `data/story.ni` → curl (current behavior) for CI checkouts without `--recurse-submodules`.
- `data/story.ni` stays gitignored. `data/graph.json` stays verbatim extraction output (all tables), the audit ground truth. Cuts live only in the Twee layer + `prune-list.json`.
- `README.md` + `justfile` document `git clone --recurse-submodules` and `git submodule update --init`.

## 4. Curated graph (starting spine, all 8 reachable)

Keep the existing progression gates (load-bearing):

- S1→S2 behind `seen_s1_prologue_blank_shoe_1`
- S2→S3 behind `seen_s2_wondering_blank_ball_1`
- S3→S4/S5/S6 behind `seen_s3_fitting_blank_theo_1`
- S4→S7, S5→S8 unconditional funnels.

Draft keep-list (~22 rows, verbatim text):

- S1-Prologue-Hub: `blank-shoe` (gate), `heirs-marriage-1`, `marriage-ball-1` + Continue→S2 + Press→S9-End-Pirates
- S2-Wondering-Hub: `blank-ball` (gate), `blank-shoe`, `blank-marriage` + Continue→S3 + Press→S9-End-Prince-Departs
- S3-Fitting-Hub: `blank-theo` (gate), `ball-shoe`, `blank-marriage` + Continue→S4/S5/S6 + Press→S9-End-Disaster
- S4 (Theodora): `blank-shoe`, `blank-lucinda` → funnel S7 → S9-End-Theodora-Marriage
- S5 (Lucinda): `blank-theodora` (+ keep existing single row) → funnel S8 → S9-End-Lucinda-Marriage
- S6 (Cinderella): `blank-ball-1`, `blank-marriage`, `blank-love` + Press→Peace / Executed / Wed
- Row passages: max 3 onward sibling links within the same scene or `Back to … Hub`. No cross-scene row links (keep `test_no_scene_skipping`).

Everything else (~80 rows) gets `prune-list.json` entries with `reason: user-cut`, `detail: 2026-09-15 curated-3 superset cut`. Existing `loop` + `user-cut` (birds) entries are preserved.

## 5. Components / files touched

- `src/glass.twee`: rewrite (hand-edit from current; no generator exists — `tools/extract.py` only builds `graph.json`). Delete `S-Hub-*`, trim hubs + rows to spine above, keep one-shot `[unless seen_*]` + vars sections for survivors, keep `[if 2 + 2 === 4]` scope terminator pattern.
- `tests/`: rewrite `test_twee.py` (drop all-subjects, assert max-3), `test_clickability.py` (guard polarity for survivors, reachability of kept rows), `test_oneshot.py` (row count = kept count, not 104), `test_hubstrike.py` (delete or assert zero `S-Hub-*`), `test_progression.py` (same gates, new HOMES), `test_reachability.py` (same 8 endings via new walk).
- `tools/extract.py` + `justfile`: submodule source priority (small edit).
- `.gitmodules`, `README.md`, `docs/bird-paths-review.md` follow-up note.

## 6. Data flow / error handling

Extract → graph (verbatim) → hand-curated Twee → Tweego build → `dist/index.html`. No new runtime state. Dead-end risk is the main failure mode: mitigated by (a) `Back to Hub` on every row, (b) unconditional Continue funnels S4→S7/S5→S8, (c) ending links unconditional on homed hubs, (d) static walk test proving all 8 endings reachable and no passage with zero onward links (except endings).

Submodule missing (no `--recurse-submodules`): extract falls back with a clear stderr message, never silently builds from stale `graph.json`.

## 7. Testing

- New: `test_max_three_story_choices` (fail on >3), `test_all_endings_reachable` (keep, must pass on spine), `test_no_dead_ends` (every non-ending has ≥1 story or navigation link), `test_source_rows_accounted` (every graph row → passage or `curated-3` prune entry).
- Updated counts replace 104 / 1638 / 71 magic numbers with kept-count constants.
- `just test` + `just build` gate Pages deploy (unchanged).

## 8. Open questions for reviewer

1. Approve approach A (curated spine) and deletion of `S-Hub-*`?
2. Approve draft keep-list as starting point (exact row slugs adjustable in plan)?
3. Confirm `vendor/glass` path and fallback behavior?
