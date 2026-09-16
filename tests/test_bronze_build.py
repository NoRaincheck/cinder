import subprocess
from pathlib import Path


def test_bronze_builds():
    subprocess.run(["tools/setup-tweego.sh"], capture_output=True, timeout=300)
    Path("dist").mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["build/tweego/tweego", "src/bronze", "-o", "dist/bronze.html"],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, r.stderr[-2000:]
    html = Path("dist/bronze.html").read_text(errors="replace")
    assert "Bronze-Start" in html
    assert "End-Bronze-Leave" in html
