import json, re
from pathlib import Path

TWEE = Path("src/glass/glass.twee").read_text()
PASSAGES = dict(re.findall(r"^::\s+(\S+)[^\n]*\n((?:(?!^::).)*)", TWEE, flags=re.M | re.S))
LINKS = {name: re.findall(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", body) for name, body in PASSAGES.items()}
GRAPH = json.load(open("data/graph.json"))
PRUNE = json.load(open("data/prune-list.json"))
SUBJECTS = ["kings-health", "heirs", "marriage", "ball", "shoe", "cinderella",
            "theo", "lucinda", "stepmother", "love", "blood", "magic", "god"]
# Twee metadata passages carry no game links by definition; exempt from link/body rules.
META = {"StoryTitle", "StoryData"}

def slug_of(r):
    if "starting" in r and "final" in r:
        raw = r["starting"] + "-" + r["final"]
    else:
        # Reactions table has topic/response/reaction-rule keys instead.
        raw = (r.get("topic") or "") + "-" + (r.get("reaction rule") or r.get("response") or "")
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    return slug or "row"

def norm(s):
    # 2026-09-15 squawk removal: passage slugs use say/cry where the
    # source-derived slug has squawk/awwk. Normalize both sides alike;
    # row keys below stay raw so exemption lists are unchanged.
    # 2026-09-15 de-birding: the examine-yourself slug drops the
    # feathers clause on both sides alike; the cracker-joke slug uses
    # cracker where the source slug has polly.
    return (s.replace("squawk", "say").replace("awwk", "cry").replace("polly", "cracker")
             .replace("properly-preened-feathers-lying-as-they-ought", "properly-groomed"))

def test_link_targets_exist():
    bad = [(p, t) for p, ts in LINKS.items() for t in ts if t not in PASSAGES]
    assert bad == [], f"dead links: {bad[:5]}"

def test_fidelity_verbatim():
    thin = [p for p, b in PASSAGES.items()
            if p.startswith("S") and p not in META and len(b.strip()) < 80]
    assert thin == [], f"passages too thin (LLM invented?): {thin[:5]}"
    # Controller ruling (2026-09-15 final-fix wave, resolving BLOCKED item 1):
    # the >=40-char verbatim assertion applies only where applicable.
    # (a) short-source: src cell < 40 chars cannot contain a 40-char run
    #     (structural impossibility), exempt with reason `short-source`.
    # (b) Task-6 polish / label-junction rows, exempt with reason `polish`
    #     (see final-fix report 2026-09-14 Task-6 violator breakdown).
    # (c) Issue-2 engine-junk rows with >= 40-char sources, exempt with
    #     reason `issue-2-followup`. Remaining Issue-2 surface in the
    #     violator list has < 40-char sources and is therefore exempt
    #     under (a) short-source instead (noted per slug below).
    # (d) any non-exempt row lacking its >= 40-char run FAILS, and any
    #     drift of the violator set vs the enumerated lists FAILS.
    POLISH_EXEMPT = {
        # Task-6 report: deliberate polish [Nice word] -> Darling.
        "Reactions:cleavage-nice-word-cleavage-you-squawk-nice-word",
        # Task-6 report: deliberate polish [A random visible woman] -> A woman.
        "Reactions:say-a-random-visible-woman-giggles-faintly",
        # Task-6 report: Topic:/Response: label lines break the 40-char window.
        "Reactions:wisdom-thought-thinking-wisdom-you-intone",
        # Task-6 report: label junction; response cell is engine text.
        "Reactions:cut-that-out-says-lucinda-obscenity-reaction-rule",
        # Task-6 report: label junction; whole-string match required.
        "Reactions:cheese-everyone-turns-to-look-at-you",
    }
    ISSUE2_EXEMPT = {        # Engine-code junk row (Issue 2 follow-up).
        "Reactions:say-response-entry-paragraph-break",
        # Engine-code junk row `say "[response entry][paragraph break]";`
        # (Issue 2 follow-up). Slug collides with two short-source rows
        # (`blank out the whole row;`, `rule succeeds;`) covered under (a).
        "Fitting Remarks:row",
    }
    SHORT_EXEMPT = {
        "Reactions:obscenity-obscenity-reaction-rule",
        "Reactions:mild-obscenity-mild-reaction-rule",
        "Reactions:silence-silence-you-squawk",
        "Reactions:kindness-awwk-kindness",
        "Reactions:now-the-player-is-disgraced",
        "Reactions:say-you-squawk-very-loudly",
        "Reactions:say-awwk-yes",
        "Reactions:say-no-you-squawk-no-no",
        "Reactions:if-turn-count-is-1",
        "Reactions:begin",
        "Reactions:say-paragraph-break",
        # Empty source (aside/code row; Issue-2 surface, exempt under (a)).
        "Reactions:say-the-prince-sits-awkwardly-on-the-couch-holding-his-glass-slipper-and-trying-to-keep-it-from-crushing-lucinda-and-theodora-have-the-ends-of-the-same-couch-and-they-are-taking-turns-seeing-who-can-bend-lowest-and-show-off-the-most-cleavage-while-the-old-lady-in-her-wing-chair-carries-on-about-nonsense-for-instance",
        "Reactions:end-if",
        "Prologue Remarks:blank-stepmother",
        # Empty comment (engine-code row; Issue-2 surface, exempt under (a)).
        "Prologue Remarks:say-the-old-woman-laughs-slightly-how-beautifully-romantic-but-she-didn-t-give-you-her-name",
        # Empty comment (engine-code row; Issue-2 surface, exempt under (a)).
        "Fitting Remarks:repeat-through-table-of-lucinda-checks",
        # Empty comment (engine-code row; Issue-2 surface, exempt under (a)).
        "Fitting Remarks:begin",
        # Slug shared with the >= 40-char Issue-2 instance above; the two
        # short instances (`blank out the whole row;`, `rule succeeds;`)
        # are exempt under (a).
        "Fitting Remarks:row",
        # Empty comment (engine-code row; Issue-2 surface, exempt under (a)).
        "Fitting Remarks:end-repeat",
        # Empty comment (engine-code row; Issue-2 surface, exempt under (a)).
        "Fitting Remarks:say-the-prince-stares-at-the-shoe-then-he-looks-up-you-he-repeats-i-mean-you-seemed-i-thought-for-certain-that-you-weren-t-the-way-you-i-thought-you-would-be-good-practice-because",
        # Empty comment (engine-code row; Issue-2 surface, exempt under (a)).
        "Cinderella Checking Remarks:if-fitting-is-happening-and-cinderella-is-the-current-subject-yes",
        # Empty comment (engine-code row; Issue-2 surface, exempt under (a)).
        "Cinderella Checking Remarks:otherwise-no",
        # Empty comment (engine-code row; Issue-2 surface, exempt under (a)).
        "Cinderella Checking Remarks:say-cinde",
        # Empty comment (engine-code row; Issue-2 surface, exempt under (a)).
        "Cinderella Checking Remarks:say-this-story-may-strike-you-as-familiar-which-means-that-you-already-have-some-idea-of-the-ways-it-can-end-up",
        # Empty comment (engine-code row; Issue-2 surface, exempt under (a)).
        "Cinderella Checking Remarks:say-inform-7-is-the-work-of-graham-nelson-and-story-title-was-compiled-using-andrew-hunter-s-compiler-for-mac-os-x",
    }
    SQUAWK_REMOVED_EXEMPT = {
        # 2026-09-15 squawk removal: this row's only >= 40-char verbatim run
        # contained "you squawk" (now "you say"). Content otherwise intact.
        "Reactions:say-oops-you-squawk-sorry-oops-sorry",
    }
    # 2026-09-15 curated-3 rescope (Task 4): the 15-row spine cut every
    # passage outside KEEP, so all full-glass violator/exempt keys above are
    # either prune-listed (skipped: cut by design) or passageless (skipped:
    # coverage is asserted by test_no_missing_rows instead). Every surviving
    # non-pruned row with a passage is verbatim-grounded, hence the
    # curated-universe constants below. The category sets above are retained
    # for provenance (git history of the 104-row glass).
    # EXPECTED_EXEMPT and EXPECTED_VIOLATOR_INSTANCES are empty because the
    # curated spine contains zero violations — every surviving passage has
    # a >=40-char verbatim run from its source row (the curation dropped all
    # thin/invented passages). If a future edit introduces a violation, these
    # constants must be updated before the test can pass.
    EXPECTED_EXEMPT = set()
    EXPECTED_VIOLATOR_INSTANCES = 0
    exempt = {}  # unique key -> reason
    viol_instances = 0
    unexpected = []
    for table, rows in GRAPH.items():
        for r in rows:
            slug = slug_of(r)
            if not slug:
                continue
            if any(e.get("table") == table and e.get("slug", slug) == slug
                   for e in PRUNE):
                continue  # user-cut/loop-pruned rows have no passage by design
            cands = [p for p in PASSAGES
                     if p.startswith("S") and p not in META and norm(slug) in norm(p.lower())]
            if not cands:
                continue  # row-to-passage coverage is asserted by test_no_missing_rows
            key = f"{table}:{slug}"
            if "comment" in r:
                src = r["comment"] or ""
            else:
                # Reactions rows use topic/response keys.
                src = " ".join([r.get("topic") or "", r.get("response") or ""])
            src = " ".join(src.split())
            if len(src) < 40:
                viol_instances += 1
                if key not in SHORT_EXEMPT:
                    unexpected.append(f"{key}:short-source-unlisted")
                else:
                    exempt.setdefault(key, "short-source")
                continue
            if any(src[i:i + 40] in " ".join(PASSAGES[p].split())
                   for p in cands for i in range(len(src) - 39)):
                continue
            viol_instances += 1
            if key in POLISH_EXEMPT:
                exempt.setdefault(key, "polish")
            elif key in ISSUE2_EXEMPT:
                exempt.setdefault(key, "issue-2-followup")
            elif key in SQUAWK_REMOVED_EXEMPT:
                exempt.setdefault(key, "squawk-removed")
            else:
                unexpected.append(key)
    assert unexpected == [], f"non-exempt rows lacking a >=40-char verbatim run: {unexpected[:10]} (total {len(unexpected)})"
    assert set(exempt) == EXPECTED_EXEMPT, (
        f"exempt set drifted: missing={sorted(EXPECTED_EXEMPT - set(exempt))[:10]} "
        f"extra={sorted(set(exempt) - EXPECTED_EXEMPT)[:10]}")
    assert viol_instances == EXPECTED_VIOLATOR_INSTANCES, (
        f"violator instance count changed: {viol_instances} != {EXPECTED_VIOLATOR_INSTANCES}")
