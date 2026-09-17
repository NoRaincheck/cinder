import subprocess
from pathlib import Path


def test_alabaster_builds():
    s = subprocess.run(["tools/setup-tweego.sh"], capture_output=True, text=True, timeout=300)
    assert s.returncode == 0, s.stderr[-2000:]
    Path("dist").mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["build/tweego/tweego", "src/alabaster", "-o", "dist/alabaster.html"],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, r.stderr[-2000:]
    p = subprocess.run(["node", "tools/patch-chapbook.js", "dist/alabaster.html"],
                       capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, p.stderr[-2000:]
    html = Path("dist/alabaster.html").read_text(errors="replace")
    assert "Alabaster-Start" in html
    assert "End-Alabaster-Sundering" in html
