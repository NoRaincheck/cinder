from pathlib import Path

import re

TWEE = Path("src/glass.twee").read_text()


def test_no_parser_artifacts():
    lowered = TWEE.lower()
    for artifact in ["[awwk]", "[nice word]", "[comment entry]"]:
        assert artifact not in lowered, f"unresolved artifact: {artifact}"
    # Bare [if guards are gone; allowed [if lines are the always-true scope
    # terminator, seen-flag progression gates, and Chapbook conditional
    # modifiers (audited in test_clickability.py).
    bad = [l.strip() for l in TWEE.splitlines()
           if "[if " in l.lower()
           and l.strip() != "[if 2 + 2 === 4]"
           and not re.fullmatch(r"\[if seen_[a-z0-9_]+\]", l.strip().lower())
           and not re.fullmatch(r"\[if [a-z]+[A-Z][a-zA-Z0-9]+\]", l.strip())]
    assert bad == [], f"unresolved artifacts: {bad[:5]}"


