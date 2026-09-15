# Bird-paths review — the 9 story paths kept in the de-birding

Commit `fcb7a1e` removed all parrot/polly/feathers *framing* but kept 9 paths
under the "relevant to, or advancing, the story" criterion. This file lists
exactly what they are so you can decide: keep, or take the nuclear option
(delete them too).

> **Decision executed 2026-09-15:** recommendation adopted — §A1, §A2, §A5
> cut (passages + hub links deleted, `user-cut` entries in
> `data/prune-list.json`); §A3, §A4, §A6, §B kept. Coverage and fidelity
> tests consult the prune list per row, so the audit trail is enforced.
>
> **Nuclear follow-up executed 2026-09-15:** the birds topic is gone
> entirely — `S-Hub-birds`, all `The birds` links, and §A3/§A4/§A6 rows
> deleted (also `user-cut`). Remaining "bird" words: 5 story-dialogue
> lines (§A3's shoe-wearer joke went with its passage; `Yes, Parrot?`
> has no bird word) — open question below.

> Note: two passages below show truncated dialogue (magic-birds, marriage-
> birds). That is the known extractor-truncation issue, not the de-birding —
> the full text is in `story.ni` and can be restored independently.

## A. Birds-topic conversation paths (6 passages — nuclear option deletes these)

### 1. `S1-Prologue-marriage-birds-1` (Prologue, marriage → birds)
> "'Do you suppose it means that marriage is for the birds?' asks Lucinda.
*Relevance: character comedy; Lucinda at her most cutting. No plot.*

### 2. `S1-Prologue-blank-birds-1` (Prologue, any → birds)
> "'I suppose it wishes to advocate a greater interest in aviary concerns?' the Prince asks, looking at you with curiosity.
*Relevance: flavor; Prince being kind to the bird. No plot.*

### 3. `S2-Wondering-blank-birds-1` (Wondering, any → birds)
> "'At least we can rule out the parrot as a possible wearer of the shoe,' says the old lady, twinkling."
*Relevance: ties the bird to the shoe plot (the fitting quest); old-lady wit. Plot-adjacent.*

### 4. `S3-Fitting-magic-birds-1` (Fitting, magic → birds)
> "All eyes turn to you. 'I have heard,' the Prince says tentatively, 'about creatures who are possessed...'
*Relevance: the possession/magic-suspicion thread — feeds the story's central danger (magic = death penalty). Plot-relevant.*

### 5. `S5-Checking-Lucinda-blank-birds-1` (Checking Lucinda, any → birds)
> "'I do believe the parrot is jealous,' remarks Theo.
*Relevance: one-line Theo beat on the road to Lucinda's endgame. Light.*

### 6. `S6-Checking-Cinderella-blank-birds-1` (Checking Cinderella, any → birds)
> "Cinderella smiles, and comes over to where you are, and pets the top of your head and whispers cossetting things in a language only you understand. Your heart is filled with sweetness."
*Relevance: the only warm Cinderella beat in the game; pays off her kindness before the finale. Emotionally load-bearing.*

## B. Parrot mentions inside non-bird passages (1 passage — nuclear option cuts the sentence, keeps the passage)

### 7. `S2-Wondering-blank-lucinda-1` (Wondering, any → Lucinda)
> "'Yes, Parrot?' asks Lucinda, looking up at you rather coldly. She's always made it clear she thinks you possessed. Theo is much nicer."
*Relevance: establishes Lucinda's coldness + the possession motif (callbacks §A4). The passage is a Lucinda path; only this sentence mentions the bird.*

(The other two parrot mentions — §A3 shoe-wearer joke, §A5 jealous — sit
inside birds-topic passages already listed above, so they go with §A if
those go.)

## What the nuclear option entails

- Delete the 6 §A passages + their `S-Hub-birds` hub + `The birds` links
  (or: keep the hub as a dead end — not recommended), cut the §B sentence.
- Test updates: coverage (`test_no_missing_rows`), all-subjects
  (`SUBJECTS` list), reachability (scenes still routable — verified: no
  scene depends solely on a birds passage), fidelity exemptions.
- `data/graph.json` stays verbatim (extraction source); deletions live in
  the Twee layer with a prune-list entry, same pattern as the loop/invalid
  prune audit.

## Recommendation

Keep §A3, §A4, §A6, §B (plot/emotion threads); §A1, §A2, §A5 are safe to
cut if you want fewer bird paths without touching the story.
