from pathlib import Path

TWEE = Path("src/glass.twee").read_text()


def test_no_parser_artifacts():
    lowered = TWEE.lower()
    for artifact in ["[if ", "[awwk]", "[nice word]", "[comment entry]"]:
        assert artifact not in lowered, f"unresolved artifact: {artifact}"


def test_attribution_present():
    assert "Emily Short" in TWEE
    assert "I7-Examples/Glass" in TWEE
    footer = "After Emily Short's Glass (I7-Examples/Glass). Choice adaptation, light polish, all paths preserved."
    assert footer in TWEE
    prologue = TWEE.split(":: Prologue-Intro", 1)[1].split("\n:: ", 1)[0]
    assert footer in prologue
