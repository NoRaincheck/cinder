import subprocess
from pathlib import Path

SRC = Path("src/glass/glass.twee")


def test_glass_moved_to_story_dir():
    assert SRC.exists(), "src/glass/glass.twee missing after split"
    assert not Path("src/glass.twee").exists(), "old path still present"


def test_patch_accepts_target_arg():
    r = subprocess.run(
        ["node", "tools/patch-chapbook.js", "--help"],
        capture_output=True, text=True, timeout=60,
    )
    assert "target" in (r.stdout + r.stderr).lower()
