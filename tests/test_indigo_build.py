import subprocess
from pathlib import Path


def test_indigo_builds():
    subprocess.run(["tools/setup-tweego.sh"], capture_output=True, timeout=300)
    Path("dist").mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["build/tweego/tweego", "src/indigo", "-o", "dist/indigo.html"],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, r.stderr[-2000:]
    p = subprocess.run(["node", "tools/patch-chapbook.js", "dist/indigo.html"],
                       capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, p.stderr[-2000:]
    html = Path("dist/indigo.html").read_text(errors="replace")
    assert "Indigo-Start" in html
    assert "End-Indigo-Escape" in html
