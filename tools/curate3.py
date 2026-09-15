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
    open(dst, "w").write("\n\n".join(out) + "\n")
    print(f"kept_rows={len(KEEP)} passages={len(out)}")

def rebuild_hub(hub, rows, ps):
    # keep first 3 story link blocks verbatim from old hub, drop S-Hub-* quads,
    # keep Continue/Press lines, append nothing else
    body = ps[hub]
    keep_lines = []
    lines = body.splitlines()
    for i, l in enumerate(lines):
        m = re.fullmatch(r"\[\[([^\]|]+)\|([^\]]+)\]\]", l.strip())
        if not m:
            continue
        label, tgt = m.group(1), m.group(2)
        if tgt in rows or label.startswith(("Continue to ", "Press on toward ")):
            prev = lines[i-1].strip() if i > 0 else ""
            if prev.startswith("["):
                keep_lines.append(prev)
            keep_lines.append(l.strip())
    head = body.split("[unless", 1)[0].split("[[", 1)[0]
    return f":: {hub}\n{head}" + "\n".join(keep_lines)

def rebuild_row(row, ps):
    body = strip_topic_quads(ps[row])
    hub = HUB_OF[scene(row)]
    # normalize the Return-to-Hub nav to a Back-to-Hub link (Back = nav, not story)
    body = body.replace("[[Return to ", "[[Back to ")
    if f"Back to" not in body:
        body = body.rstrip() + f"\n[[Back to the talk|{hub}]]\n"
    return f":: {row}\n{body}"

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
