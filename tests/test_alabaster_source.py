import json
from pathlib import Path

SRC = Path("ref/source/alabaster.txt")


def test_alabaster_source_vendored():
    assert SRC.exists(), "ref/source/alabaster.txt missing"
    assert SRC.stat().st_size > 100_000, "alabaster.txt suspiciously small"
    text = SRC.read_text(errors="replace")
    assert '"Alabaster" by' in text
    assert "Part 10 - Endings" in text


def test_alabaster_graph_schema():
    g = json.loads(Path("data/alabaster-graph.json").read_text())
    assert g["rooms"] == ["Dark Woods", "Castle", "Safe Haven"]
    assert len(g["passages"]) == 25
    assert len(g["endings"]) == 11
    assert set(g["endings"]) <= set(g["passages"])


def test_alabaster_prune_reasons_valid():
    prune = json.loads(Path("data/alabaster-prune-list.json").read_text())
    assert prune, "prune list must not be empty"
    for e in prune:
        assert e["reason"] in {"loop", "invalid-input", "user-cut"}, e
        assert e["detail"], e


def test_alabaster_extraction_report():
    r = json.loads(Path("data/alabaster-extraction-report.json").read_text())
    assert r["method"] == "manual transcription from source read"
    assert r["rooms"] == 3
