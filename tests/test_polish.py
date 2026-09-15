from pathlib import Path

import re

TWEE = Path("src/glass.twee").read_text()


def test_no_parser_artifacts():
    lowered = TWEE.lower()
    for artifact in ["[awwk]", "[nice word]", "[comment entry]"]:
        assert artifact not in lowered, f"unresolved artifact: {artifact}"
    # Bare [if guards are gone; allowed [if lines are the always-true scope
    # terminator and seen-flag progression gates (Chapbook-native, audited
    # in test_clickability.py).
    bad = [l.strip() for l in TWEE.splitlines()
           if "[if " in l.lower()
           and l.strip() != "[if 2 + 2 === 4]"
           and not re.fullmatch(r"\[if seen_[a-z0-9_]+\]", l.strip().lower())]
    assert bad == [], f"unresolved artifacts: {bad[:5]}"


