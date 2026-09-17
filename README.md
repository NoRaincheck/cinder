# Cinder

Choice-based Twine ports of Emily Short's Inform 7 games **Glass**,
**Bronze**, and **Indigo** (originals: [I7-Examples/Glass](https://github.com/I7-Examples/Glass),
[I7-Examples/Bronze](https://github.com/I7-Examples/Bronze)).
A landing page links all three stories. In Glass you steer the drawing-room
talk: free-text `mention [subject]` from the parser original becomes
clickable subject choices. All narrative paths are preserved — only
looping filler and invalid-input handlers were pruned (audited in
`data/prune-list.json`).

## Try it locally (from a build)

Prereqs: [`just`](https://just.systems) and `python3`. Then:

```bash
just preview
```

The Inform 7 sources live at `ref/source/glass.ni` and
`ref/source/bronze.ni` (committed).

This installs the pinned toolchain (Tweego 2.1.1 + Chapbook 2.3.0),
compiles `src/glass/` → `dist/glass.html`, `src/bronze/` →
`dist/bronze.html`, generates the landing `dist/index.html`, and serves
`dist/`. Open the printed URL (default <http://localhost:8765>) — the
landing is at `/`, the stories at `/glass.html` and `/bronze.html`.
In Glass start at *Start*, pick a subject like Heirs, and follow the
conversation to one of 5 endings.

Other recipes (`just` with no args lists them):

| Recipe                              | What it does                                                                                            |
|-------------------------------------|---------------------------------------------------------------------------------------------------------|
| `just setup`                        | Install pytest pins + fetch Tweego/Chapbook                                                             |
| `just build`                        | Compile all three stories + landing → `dist/`                                                           |
| `just build-glass`                  | Compile Glass story dir → `dist/glass.html`                                                             |
| `just build-bronze`                 | Compile Bronze story dir → `dist/bronze.html`                                                           |
| `just build-indigo`                 | Compile Indigo story dir → `dist/indigo.html`                                                           |
| `just build-landing`                | Generate landing `dist/index.html` linking all three stories                                            |
| `just test`                         | Run the full pytest suite (46 tests)                                                                    |
| `just extract [glass\|bronze\|all]` | Re-parse `ref/source/*.ni` → `data/*graph.json` + prune audits (glass/bronze only; indigo.t3 is manual) |
| `just preview`                      | Build + serve `dist/` locally for playtesting                                                           |
| `just clean`                        | Remove `dist/`, `build/`, caches                                                                        |

## Layout

```
src/glass/glass.twee    Chapbook 2 source — 30 story passages + 2 meta, a curated linear spine
src/bronze/bronze.twee  Chapbook 2 source — Bronze curated spine, all passages Bronze- prefixed
src/indigo/indigo.twee  Chapbook 2 source — Indigo curated spine, all passages Indigo- prefixed
tools/extract.py      Parses ref/source/glass.ni remark tables → data/graph.json;
                      scans ref/source/bronze.ni rooms/tables → data/bronze-graph.json
tools/build-landing.py Renders story cards into dist/index.html landing page
tools/setup-tweego.sh Fetches pinned Tweego + Chapbook binaries
tools/polish.md       LLM rules: light polish only, verbatim kept, FLAG don't rewrite
data/                 graph.json, prune-list.json, extraction-report.json
                       (+ bronze-graph.json, bronze-prune-list.json, bronze-extraction-report.json)
                       (+ indigo-graph.json, indigo-prune-list.json, indigo-extraction-report.json)
tests/                toolchain, extract, link integrity, reachability, build, polish,
                      bronze graph/source/extract/build, landing, multi-artifact patch
dist/                 Build output (gitignored) — index.html landing + glass.html + bronze.html + indigo.html
```

## How the port works

1. `just extract` parses the six remark tables (Prologue, Wondering, Fitting,
   Theodora/Lucinda/Cinderella Checking) into a subject graph.
2. Each row becomes a passage; every conversation passage links all 14
   subjects (missing-row moves fall back to the scene's generic redirect,
   faithful to the original's "uncomfortable silence").
3. One-shot links: each row passage sets a `seen_*` flag in a leading vars
   section, and links to visited rows hide behind `[unless seen_*]` guards —
   like the original blanking each remark after use. Subject-hub links show
   visited hubs struck-through instead of hiding (hub pages must never
   empty out). Hub/ending links stay unconditional so navigation can never
   vanish.
4. Scene gating: the start opens only the Prologue; Wondering unlocks behind
   the shoe discussion, Fitting behind the ball, the Checking scenes behind
   Theo, and each ending lives in exactly one scene — so the evening always
   moves forward and every ending stays reachable.
5. `just build` compiles each story dir to `dist/glass.html` /
   `dist/bronze.html` plus the landing `dist/index.html`; pushing `main`
   deploys `dist/` to GitHub Pages via `.github/workflows/pages.yml`
   (pytest gate included).

## Attribution

Original game **Glass** by Emily Short (Inform 7 example, 2006). This is a
choice adaptation with light polish — dialogue kept verbatim except parser
artifacts; see the footer on the start passage. Dated content is flagged for
editorial review, never silently rewritten.

## Known deviations

- **Bird layer removed:** no `squawk`/`awwk`/`parrot`/`polly`/`feathers`
  framing and no birds topic — no `The birds` links, no `S-Hub-birds`, none
  of the 9 birds-topic passages remain (3 flavor cuts + 6 topic rows, all
  audited as `user-cut` in `data/prune-list.json`).
  Still present, awaiting your call: 5 story-dialogue lines containing the
  word "bird" (`For a bird…`, `Stupid bird`, `Your bird, madam…`,
  `bird school`, `One at a time, bird`) — see `docs/bird-paths-review.md`.
  Also kept: the wing chair (furniture).
  (`data/graph.json` still mirrors the original text verbatim as the
  extraction source.)
