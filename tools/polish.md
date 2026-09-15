# Polish prompt (Task 6 LLM polish gate)

Use this prompt when a human or model reviews one ported passage at a time.
A deterministic scripted implementation of these rules lives outside the repo
(one-shot pass); this document is the normative rule set it implements.

## Input

One `data/graph.json` row: its `starting`, `final`, `comment` fields
(or `topic` / `response` / `reaction rule` for Reactions-table rows),
plus the current twee passage body for that row.

## Output

- A choice label of at most 6 words, in the parrot's voice.
- A passage body that is ~95% verbatim from the source row: keep every
  line of dialogue and narration exactly as written. Fix only the
  parser artifacts listed below. Never invent plot, dialogue, or stage
  business.
- If a passage carries dated content (for example the "cleavage" gag),
  do NOT silently rewrite it. Keep the text and append a line:

  `<!-- FLAG: <reason> -->`

  so a human decides (keep verbatim, soften, or cut) before merge.

## Artifact resolutions (deterministic, grounded in `data/story.ni`)

| Artifact | Resolution | Grounding |
|---|---|---|
| `{set currentSubject to '...'}` whole line | Delete the line. Chapbook 2.3.0 has no `set` insert or modifier (`build/tweego/storyformats/chapbook-2/format.js`: 15 inserts, 8 modifiers, none named `set`); unknown `{...}` renders literally into the page, and nothing ever reads the variable. | engine source + `dist/index.html` leak |
| `[awwk]` | `Awwk` (first row of the Table of Awwkwardness) | `story.ni` Table of Awwkwardness |
| `you awwk` (bare, in parrot table text) | `you squawk` | `To say awwk` say-phrase; plain-text reading |
| `[Nice word]` / `[nice word]` | `Darling` (first row of the Table of Flattery) | `story.ni` `To say nice word` |
| `[if ...]` guard with a single branch | Drop the marker, keep the visible text (the extractor already selected this path's text; no Chapbook equivalent exists) | remark rows in `story.ni` |
| `[if mentioning Lucinda]A[otherwise]B[end if]C` | `AC` when the passage subject is Lucinda (true-branch); drop the false-branch | `story.ni` Fitting Remarks |
| `say "[response entry][paragraph break]".` / `say paragraph break;` whole line | Delete the line (runtime table-selection with no static text; the bridge narration carries the passage) | `story.ni` relate/instructions rules |
| `[obscenity]` in a Topic line | `an obscenity` | `story.ni` Understand-as-obscenity lines |
| `[mild obscenity]` in a Topic line | `a mild obscenity` | `story.ni` Understand-as-mild lines |
| `[A random visible woman]` | `A woman` (never name *which* woman; that would invent plot) | `story.ni` random-woman phrase |

## Attribution

`Prologue-Intro` ends with this footer, verbatim:

After Emily Short's Glass (I7-Examples/Glass). Choice adaptation, light polish, all paths preserved.

## Constraints (global)

- Chapbook 2 only, no custom JS.
- Light polish only: every passage must keep a >= 40-char verbatim run
  of its pre-polish body, stay >= 80 chars overall, and keep all links.
- Full suite (`python3 -m pytest tests/ -v`) must stay green.
