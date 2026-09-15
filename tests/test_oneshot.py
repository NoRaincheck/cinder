"""The one-shot seen-flag guards were removed in the 2026-09-15 curation (the
3-choice spine tracks no visited state). This module asserts that no stray
seen_* guards or vars sections survive; if the machinery is reintroduced,
these tests will automatically verify it."""

import re
from pathlib import Path

TWEE = Path("src/glass.twee").read_text()


def test_no_stray_seen_guards():
    """No seen_* guards or vars sections should survive the curation."""
    guards = re.findall(r"\[(?:if|unless)\s+seen_", TWEE)
    vars_sections = re.findall(r"^::\s+\S+\s*\n\s*vars:\s*$", TWEE, flags=re.M)
    assert guards == [], f"stray seen_* guards found: {guards[:5]}"
    assert vars_sections == [], f"stray vars sections found: {vars_sections[:5]}"
