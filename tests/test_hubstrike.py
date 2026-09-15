"""Subject hubs removed: the 3-choice spine (2026-09-15) cut all `S-Hub-*`
subject-hub passages; scene hubs stay always-clickable."""
import re
from pathlib import Path

TWEE = Path("src/glass.twee").read_text()
PASSAGES = dict(re.findall(r"^::\s+(\S+)[^\n]*\n((?:(?!^::).)*)", TWEE, flags=re.M | re.S))


def test_no_subject_hubs():
    assert [n for n in PASSAGES if n.startswith("S-Hub-")] == []
