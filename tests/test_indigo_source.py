import hashlib
import json
from pathlib import Path

SRC = Path("ref/source/indigo.t3")
SHA256 = "3ddaa5071e599805232cb6c4526223d0f24907cd6747eb09c104cd25894bafab"


def test_indigo_source_vendored():
    assert SRC.exists(), "ref/source/indigo.t3 missing"
    assert SRC.stat().st_size > 100_000, "indigo.t3 suspiciously small"
    blob = SRC.read_bytes()
    assert blob[:8] == b"T3-image", "not a TADS3 image"
    assert hashlib.sha256(blob).hexdigest() == SHA256, "indigo.t3 corrupted"


def test_indigo_graph_schema():
    g = json.loads(Path("data/indigo-graph.json").read_text())
    assert g["rooms"] == ["Kitchen", "Blue Tower", "Store Room", "At the Foot of the Tower"]
    assert len(g["passages"]) == 20
    assert g["endings"] == ["End-Indigo-Escape", "End-Indigo-Spoiled"]
    assert set(g["endings"]) <= set(g["passages"])


def test_indigo_prune_reasons_valid():
    prune = json.loads(Path("data/indigo-prune-list.json").read_text())
    assert prune, "prune list must not be empty"
    for e in prune:
        assert e["reason"] in {"loop", "invalid-input", "user-cut"}, e
        assert e["detail"], e


def test_indigo_extraction_report():
    r = json.loads(Path("data/indigo-extraction-report.json").read_text())
    assert r["method"] == "manual transcription from live play"
    assert r["rooms"] == 4
