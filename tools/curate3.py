"""Filter src/glass.twee to the curated 3-choice spine. Keeps passage bodies
verbatim; rewrites hub link blocks to <=3 story links + Back/Continue/Press nav;
drops S-Hub-* passages; appends Back-to-Hub to every kept row."""
import re, sys

KEEP = [
    "S1-Prologue-blank-shoe-1", "S1-Prologue-heirs-marriage-1", "S1-Prologue-marriage-ball-1",
    "S2-Wondering-blank-shoe-1", "S2-Wondering-blank-ball-1", "S2-Wondering-blank-marriage-1",
    "S3-Fitting-ball-shoe-1", "S3-Fitting-blank-marriage-1", "S3-Fitting-blank-theo-1",
    "S4-Checking-Theodora-blank-lucinda-1", "S4-Checking-Theodora-blank-shoe-1",
    "S5-Checking-Lucinda-blank-theodora-1",
    "S6-Checking-Cinderella-blank-ball-1", "S6-Checking-Cinderella-blank-marriage-1",
    "S6-Checking-Cinderella-blank-love-1",
]
HUB_OF = {"S1": "S1-Prologue-Hub", "S2": "S2-Wondering-Hub", "S3": "S3-Fitting-Hub",
          "S4": "S4-Checking-Theodora-Hub", "S5": "S5-Checking-Lucinda-Hub",
          "S6": "S6-Checking-Cinderella-Hub"}

def scene(n):
    m = re.match(r"(S\d)-", n)
    return m.group(1) if m else None

def strip_topic_quads(body):
    # Drop the 4-line topic blocks tied to removed S-Hub-* passages:
    #   [if seen_hub_X] / ~~Label~~ / [else] / [[Label|S-Hub-X]]
    # Leaves narrative, vars headers, guards, and hub/Continue/Press nav intact.
    out = []
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        if re.fullmatch(r"\[if seen_hub_[^\]]+\]", lines[i].strip()):
            j = i + 1
            # expect ~~struck~~, [else], S-Hub link; skip whatever matches that shape
            if j < len(lines) and lines[j].strip().startswith("~~"):
                j += 1
            if j < len(lines) and lines[j].strip() == "[else]":
                j += 1
            if j < len(lines) and "S-Hub-" in lines[j]:
                j += 1
            i = j
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)

def relabel_nav(passage):
    # Final pass: every non-story link renders as bare `>` (no ending or
    # return-to info); drop exact-duplicate link lines.
    name, _, body = passage.partition("\n")
    seen, out = set(), [name]
    for l in body.splitlines():
        m = re.fullmatch(r"\[\[([^\]|]+)\|([^\]]+)\]\]", l.strip())
        if m and not m.group(1).startswith("Steer toward"):
            l = f"[[>|{m.group(2)}]]"
            if l in seen:
                continue
            seen.add(l)
        out.append(l)
    return "\n".join(out)

def main(src, dst):
    t = open(src).read()
    ps = dict(re.findall(r"^::\s+(\S+)[^\n]*\n((?:(?!^::).)*)", t, flags=re.M | re.S))
    # hub story targets per spec spine
    spine = {
        "S1-Prologue-Hub": KEEP[0:3], "S2-Wondering-Hub": KEEP[3:6],
        "S3-Fitting-Hub": KEEP[6:9],
        "S4-Checking-Theodora-Hub": KEEP[9:11], "S5-Checking-Lucinda-Hub": KEEP[11:12],
        "S6-Checking-Cinderella-Hub": KEEP[12:15],
    }
    out = []
    for name in ["StoryTitle", "StoryData"]:
        out.append(f":: {name}\n{ps[name]}")
    out.append(f":: Prologue-Intro\n{strip_topic_quads(ps['Prologue-Intro'])}")
    for hub, rows in spine.items():
        out.append(rebuild_hub(hub, rows, ps))
    for r in KEEP:
        out.append(rebuild_row(r, ps))
    for hub in ["S7-Theodora-Endgame-Hub", "S8-Lucinda-Endgame-Hub"]:
        out.append(f":: {hub}\n{strip_topic_quads(ps[hub])}")
    for e in [n for n in ps if "-End-" in n]:
        out.append(f":: {e}\n{ps[e]}")
    out = [relabel_nav(p) for p in out]
    open(dst, "w").write("\n\n".join(out) + "\n")
    print(f"kept_rows={len(KEEP)} passages={len(out)}")

def rebuild_hub(hub, rows, ps):
    # keep first 3 story link blocks verbatim from old hub, drop S-Hub-* quads,
    # keep Continue/Press lines as bare `>` nav, dedupe identical nav targets.
    # All navigation renders as `>` (no ending/return info).
    body = ps[hub]
    keep_lines, nav_seen, nav_out = [], set(), []
    lines = body.splitlines()
    for i, l in enumerate(lines):
        m = re.fullmatch(r"\[\[([^\]|]+)\|([^\]]+)\]\]", l.strip())
        if not m:
            continue
        label, tgt = m.group(1), m.group(2)
        if tgt in rows:
            prev = lines[i-1].strip() if i > 0 else ""
            if prev.startswith("[") and not prev.startswith("[["):
                keep_lines.append(prev)
            keep_lines.append(l.strip())
        elif label.strip() == ">" or label.startswith(("Continue to ", "Press on toward ", "Back to ", "Take up ")):
            prev = lines[i-1].strip() if i > 0 else ""
            if tgt not in nav_seen:
                nav_seen.add(tgt)
                nav_out.append((prev if prev.startswith("[") and not prev.startswith("[[") else None, tgt))
    if nav_out and rows:
        # Terminate the last [unless]/[if] scope before trailing nav:
        # Chapbook modifiers leak onto all following text, so an
        # unterminated story guard would swallow the funnel/ending links.
        keep_lines.append("[if 2 + 2 === 4]")
    for guard, tgt in nav_out:
        if guard:
            keep_lines.append(guard)
        keep_lines.append(f"[[>|{tgt}]]")
    head = body.split("[unless", 1)[0].split("[[", 1)[0]
    return f":: {hub}\n{head}" + "\n".join(keep_lines)

def rebuild_row(row, ps):
    body = strip_topic_quads(ps[row])
    hub = HUB_OF[scene(row)]
    # normalize the Return-to-Hub nav to a bare `>` Back link (Back = nav, not story)
    body = body.replace("[[Return to ", "[[Back to ")
    body = re.sub(r"\[\[[^\]|]+\|(" + re.escape(hub) + r")\]\]", r"[[>|\1]]", body)
    if hub not in body:
        body = body.rstrip() + f"\n[[>|{hub}]]\n"
    return f":: {row}\n{body}"

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
