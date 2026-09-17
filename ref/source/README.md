Upstream sources:
- Glass: https://github.com/I7-Examples/Glass/blob/main/Glass.inform/Source/story.ni → `glass.ni`
- Bronze: https://github.com/I7-Examples/Bronze/blob/main/Bronze.inform/Source/story.ni → `bronze.ni`
- Indigo: https://www.ifarchive.org/if-archive/games/tads/indigo.t3 → `indigo.t3`

Local copies are renamed from upstream `story.ni` for clarity.
Extraction reads them directly (`just extract [glass|bronze|all]`); the snapshot
URLs above only restore a copy if missing.
`indigo.t3` is the compiled TADS3 image (no `.ni` source; text is compressed, so extraction is manual transcription, not `just extract`).
