from pathlib import Path

SRC = Path("ref/source/bronze.ni")


def test_bronze_source_vendored():
    assert SRC.exists(), "ref/source/bronze.ni missing"
    assert SRC.stat().st_size > 100_000, "bronze.ni suspiciously small"


def test_bronze_source_header():
    text = SRC.read_text(encoding="utf-8", errors="replace")
    assert '"Bronze" by Emily Short' in text
