import subprocess
from pathlib import Path

# Toolchain channel: official Tweego 2.1.1 release binary (GitHub) + Chapbook
# 2.3.0 story format (klembot.github.io), bootstrapped by tools/setup-tweego.sh.
# The `npx tweego@2.1.1` channel is dead (npm registry 404) — see task-5 report.
TWEEGO = Path("build/tweego/tweego")


def test_tweego_builds_index():
    setup = subprocess.run(["tools/setup-tweego.sh"],
                           capture_output=True, text=True, timeout=300)
    assert setup.returncode == 0, setup.stderr[-2000:]
    assert TWEEGO.exists(), "tweego binary missing after setup"
    Path("dist").mkdir(parents=True, exist_ok=True)
    r = subprocess.run([str(TWEEGO), "src", "-o", "dist/index.html"],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr[-2000:]
    html = Path("dist/index.html")
    assert html.exists() and html.stat().st_size > 50_000
    text = html.read_text(errors="replace")
    # Curated 3-choice spine (2026-09-15): the start passage is "Start" and
    # endings are named End-<Name> (no S9-/S-Hub- scaffolding remains).
    assert "Start" in text
    for end in ["End-Cinderella-Wed", "End-Lucinda-Marriage", "End-Peace"]:
        assert end in text, f"ending missing from build: {end}"
