# Twee-Glass Design Spec

**Date:** 2026-09-14
**Source:** https://github.com/I7-Examples/Glass (`Glass.inform/Source/story.ni`, 71193 bytes)
**Target repo:** `twee-glass` (empty except `.git`, `.gitignore`), GitHub Pages static site
**Story format:** Chapbook 2 via Tweego (least custom code, literary fidelity)

## 1. Goal

Port Emily Short's Inform 7 parser game Glass to Twine Twee (Chapbook) as
choice-based static HTML. Player is the parrot; free-text `mention [subject]`
becomes clickable subject choices. LLM does light polish only (fix parser
artifacts, generate ≤6-word choice labels). All narrative paths preserved.

## 2. Scope rule (user constraint)

Encode and maintain ALL paths. The ONLY removals allowed:

1. **Loop rows** — repeat-of-current-subject scolds (`Table of Bad Bird Excuses`,
   4 rows), one-shot rows already consumed (original `blank out the whole row`
   behavior), `Table of Waiting` filler (8 rows), `Table of Awwkwardness`
   (5 rows), `Table of Insults` (15 rows) / `Table of Flattery` (7 rows) random
   variation beyond one representative passage each.
2. **Invalid-input handlers** — `jungle crying` unknown-topic fallback, directed
   speech errors (`ask X about Y` → "only squawk for everyone"), scenery/physical
   action stubs (take, go, kiss, eat, etc.), `poop/preen/fly/peck` jokes beyond
   one representative each, obscenity → pirate-sale kept as ONE ending only.

Everything else ships: every subject-pair remark, every scene, every ending.

## 3. Source inventory (ground truth = `story.ni`, verified 2026-09-14)

**Conversation tables (must all be extracted):** Prologue Remarks, Wondering
Remarks, Fitting Remarks, Theodora Checking Remarks, Lucinda Checking Remarks,
Cinderella Checking Remarks, Reactions (kept: cracker, seven, silence, wisdom,
kindness, almond, cheese, fire, cleavage, prying; pirate row maps to the single
obscenity ending).

**Table count (live source truth, `data/extraction-report.json`):** 14
`Table of ...` blocks in `story.ni` — the 7 conversation tables above plus
Bad Bird Excuses, Waiting, Awwkwardness, Insults, Flattery, Lucinda Checks,
and Theodora Checks.

**Scenes (must all be routable):** Prologue → Wondering → Fitting →
Checking Theodora / Checking Lucinda / Checking Cinderella → Theodora Endgame
(ends in Theodora Marriage) / Lucinda Endgame (ends in Lucinda Marriage) /
ends in peace / ends in disaster (current subject is magic) / Prince departs in
anger / Cinderella executed / Cinderella+Prince wed / pirate sale
("You are sold to pirates and have a glorious career on the open sea").
Bird trouble (disgraced 2-minute timer) collapses to a single scold passage,
no timer.

**Subjects (canonical list resolved by extractor, expected ~14 + blank):**
king's health, heirs, marriage, ball, shoe, Cinderella, Theo, Lucinda,
stepmother, love, blood, magic, god, birds, blank (wildcard matcher).
`blank` is never a clickable choice; it is a fallback matcher.

## 4. Passage model (Chapbook, minimal code)

- Twee 3 source in `src/glass.twee`. `StoryData`: `{"format": "Chapbook-2",
  "start": "Prologue-Intro"}`. No custom JS.
- One passage per remark row: `:: S2-Wondering blank->ball ["Mention the ball"]`,
  body = original `comment` text lightly polished. Passage names are
  `S<scene#>-<Scene> <starting>-><final>` slugified, unique.
- **Full connectivity:** every conversation passage lists a choice link for
  EVERY subject (all-paths rule). Subjects with a table row go to that row's
  passage; subjects with no row go to the scene's generic redirect passage
  (faithful to original "uncomfortable silence / Mm, we were speaking of X"
  + NPC suggestion-path advance). No dead links except terminal endings.
- **One-shot blanking without loops:** first visit shows full remark; repeat
  visit routes to `<passage>-revisited` generic ("already discussed, conversation
  moves on") instead of deleting the link. Links never disappear, so no dead
  ends are introduced.
- **Scene gates:** scene-advance conditions from original (`Prologue ends when
  current subject is shoe`, `Wondering ends when current is ball`, Fitting
  target Theo, Checking* conditions) become explicit `[[Continue|...]]` forks
  after the triggering passage. `currentSubject` tracked via Chapbook vars
  (`{set currentSubject to 'shoe'}`) — the only state, no other mechanics.
- **Parrot voice:** header shows `discussing {currentSubject}` (replaces status
  line). Choice labels in parrot voice ("Squawk about heirs!"), body keeps
  Emily Short dialogue verbatim except parser artifacts (`[if mentioning X]`,
  `[awwk]`, `[nice word]`) resolved to plain text.
- **Attribution footer** on start passage + README: original by Emily Short,
  Inform 7 example, link to `I7-Examples/Glass`, note "choice adaptation, light
  polish, all paths preserved".

## 5. LLM pipeline constraints

Prompt in `tools/polish.md`. Rules: do not invent plot/characters/endings; keep
95% verbatim; only fix parser conditionals, second-person artifacts, andchoice
labels; flag dated content (e.g. cleavage gag) with `<!-- FLAG: ... -->` for
human decision, never silently rewrite; every LLM output reviewed in diff
before acceptance. Deterministic: inputs are `graph.json` rows, outputs are
passage bodies, one file per row under `build/passages/` for review.

## 6. Static site

Tweego compiles `src/*.twee` → `dist/index.html`. GitHub Actions workflow
`.github/workflows/pages.yml`: install Tweego 2.1.1 + Chapbook 2.3.0 story
format, build, upload Pages artifact, deploy on `main` push. No build output
committed except via artifact; `dist/` gitignored.

## 7. Testability requirements

Every behavior below has an automated check in `tests/` running in CI without
a browser (browser smoke optional):

1. `graph.json` contains every row of the 6 remark tables + kept Reactions rows
   (row counts asserted against extractor fixture AND full-source counts
   recorded at extraction time in `data/extraction-report.json`).
2. Prune audit: `data/prune-list.json` lists exactly the removed rows with
   reason `loop` or `invalid-input`; test asserts no remark-table row is
   missing from either `src/glass.twee` or `prune-list.json` (i.e. nothing
   silently dropped).
3. Link integrity: every `[[...|Passage]]` / `[[Passage]]` target exists; every
   non-terminal passage has ≥1 outbound choice; every subject appears as a
   choice on every conversation passage (all-paths).
4. Reachability: graph walk from `Prologue-Intro` reaches all 8+ endings and
   all 9 scenes (asserted list in test).
5. Fidelity: each passage body contains a ≥40-char verbatim substring of its
   source `comment` (guards against LLM invention); no `[if ` / `[awwk]`
   artifacts remain.
6. Build: `tweego` compiles with exit 0, `dist/index.html` exists, >50KB, and
   contains `Prologue-Intro` + each ending name.
