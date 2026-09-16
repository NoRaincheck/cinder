from pathlib import Path
from tools.extract import scan_bronze

SRC = Path("ref/source/bronze.ni")


def test_bronze_rooms_found():
    text = SRC.read_text(encoding="utf-8", errors="replace")
    result = scan_bronze(text)
    for room in ["Drawbridge", "Entrance Hall", "Central Courtyard"]:
        assert room in result["rooms"], f"room missing: {room}"


def test_bronze_tables_found():
    text = SRC.read_text(encoding="utf-8", errors="replace")
    result = scan_bronze(text)
    assert result["tables"], "no tables detected"
    assert sum(result["tables"].values()) > 10
