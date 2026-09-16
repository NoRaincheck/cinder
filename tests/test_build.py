import subprocess
from pathlib import Path

# Toolchain channel: official Tweego 2.1.1 release binary (GitHub) + Chapbook
# 2.3.0 story format (klembot.github.io), bootstrapped by tools/setup-tweego.sh.
# The `npx tweego@2.1.1` channel is dead (npm registry 404) — see task-5 report.
TWEEGO = Path("build/tweego/tweego")


def test_tweego_builds_both_stories_and_landing():
    setup = subprocess.run(["tools/setup-tweego.sh"],
                           capture_output=True, text=True, timeout=300)
    assert setup.returncode == 0, setup.stderr[-2000:]
    assert TWEEGO.exists(), "tweego binary missing after setup"
    Path("dist").mkdir(parents=True, exist_ok=True)
    for src, out in [("src/glass", "dist/glass.html"),
                     ("src/bronze", "dist/bronze.html")]:
        r = subprocess.run([str(TWEEGO), src, "-o", out],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr[-2000:]
        p = subprocess.run(["node", "tools/patch-chapbook.js", out],
                           capture_output=True, text=True, timeout=60)
        assert p.returncode == 0, p.stderr[-2000:]
    r = subprocess.run(["python3", "tools/build-landing.py"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-2000:]

    glass = Path("dist/glass.html")
    assert glass.exists() and glass.stat().st_size > 50_000
    gtext = glass.read_text(errors="replace")
    # Canonical Glass endings (glass.ni): Cinderella-wed/peace,
    # Cinderella-executed/disaster, Lucinda-Marriage (+ Prince-Departs,
    # Theodora-Marriage asserted via link integrity/reachability).
    assert "Glass" in gtext
    assert "Start" in gtext
    for end in ["End-Cinderella-Wed", "End-Lucinda-Marriage", "End-Cinderella-Executed"]:
        assert end in gtext, f"ending missing from glass build: {end}"

    bronze = Path("dist/bronze.html")
    assert bronze.exists() and bronze.stat().st_size > 50_000
    btext = bronze.read_text(errors="replace")
    assert "Bronze" in btext
    assert "Bronze-Start" in btext
    assert "End-Bronze-Leave" in btext

    landing = Path("dist/index.html").read_text(errors="replace")
    assert 'href="glass.html"' in landing
    assert 'href="bronze.html"' in landing
