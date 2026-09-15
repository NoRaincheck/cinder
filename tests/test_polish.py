from pathlib import Path

TWEE = Path("src/glass.twee").read_text()


def test_no_parser_artifacts():
    lowered = TWEE.lower()
    for artifact in ["[if ", "[awwk]", "[nice word]", "[comment entry]"]:
        assert artifact not in lowered, f"unresolved artifact: {artifact}"


def test_attribution_present():
    assert "Emily Short" in TWEE
    assert "I7-Examples/Glass" in TWEE
