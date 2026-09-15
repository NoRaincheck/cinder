# Twee-Glass

A choice-based Twine port of **Glass**, Emily Short's Inform 7 conversation
game (original: [I7-Examples/Glass](https://github.com/I7-Examples/Glass)).
You steer the drawing-room talk: free-text `mention [subject]` from the
parser original becomes clickable subject choices. All narrative paths are preserved — only
looping filler and invalid-input handlers were pruned (audited in
`data/prune-list.json`).

## Try it locally (from a build)

Prereqs: [`just`](https://just.systems) and `python3`. Then:

```bash
just preview
```

This installs the pinned toolchain (Tweego 2.1.1 + Chapbook 2.3.0), compiles
`src/*.twee` to `dist/index.html`, and serves it. Open the printed URL
(default <http://localhost:8080>) and play — start at *Prologue-Intro*,
pick a subject like Heirs, and follow the conversation to one of 8 endings.

Other recipes (`just` with no args lists them):

| Recipe         | What it does                                              |
|----------------|-----------------------------------------------------------|
| `just setup`   | Install pytest pins + fetch Tweego/Chapbook               |
| `just build`   | Compile Twee → `dist/index.html`                          |
| `just test`    | Run the full pytest suite (15 tests)                      |
| `just extract` | Re-parse `story.ni` → `data/graph.json` + prune audit     |
| `just preview` | Build + serve `dist/` locally for playtesting             |
| `just clean`   | Remove `dist/`, `build/`, caches                          |

## Layout

```
src/glass.twee        Chapbook 2 source — 143 passages, one per remark row
tools/extract.py      Parses story.ni remark tables → data/graph.json
tools/setup-tweego.sh Fetches pinned Tweego + Chapbook binaries
tools/polish.md       LLM rules: light polish only, verbatim kept, FLAG don't rewrite
data/                 graph.json, prune-list.json, extraction-report.json
tests/                toolchain, extract, link integrity, reachability, build, polish
dist/                 Build output (gitignored) — deploy artifact for Pages
```

## How the port works

1. `just extract` parses the six remark tables (Prologue, Wondering, Fitting,
   Theodora/Lucinda/Cinderella Checking) into a subject graph.
2. Each row becomes a passage; every conversation passage links all 14
   subjects (missing-row moves fall back to the scene's generic redirect,
   faithful to the original's "uncomfortable silence").
3. `just build` compiles to a single `index.html`; pushing `main` deploys it
   to GitHub Pages via `.github/workflows/pages.yml` (pytest gate included).

## Attribution

Original game **Glass** by Emily Short (Inform 7 example, 2006). This is a
choice adaptation with light polish — dialogue kept verbatim except parser
artifacts; see the footer on the start passage. Dated content is flagged for
editorial review, never silently rewritten.

## Known deviations

- **Bird layer removed:** no `squawk`/`awwk`/`parrot`/`polly`/`feathers`
  wording anywhere in play — labels are subject display names, bodies use
  `say`/`speak`/`sing`, the Polly joke is a nameless cracker joke.
  Deliberately kept: 2 story-dialogue lines where NPCs mention the parrot
  (shoe-wearer joke, Lucinda's `Yes, Parrot?`) and the plot-bearing
  birds-topic paths (possession thread, Cinderella's warm beat).
  Cut as flavor: 3 birds-topic passages (Lucinda's quip, Prince's aviary
  joke, Theo's jealous one-liner) — audited as `user-cut` rows in
  `data/prune-list.json`. Also kept: the wing chair (furniture).
  (`data/graph.json` still mirrors the original text verbatim as the
  extraction source.)
