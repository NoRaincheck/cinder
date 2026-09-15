from tools.extract import extract_tables, apply_prune_rules

FIXTURE = open("tests/fixtures/story_excerpt.ni").read()

def test_extracts_all_six_remark_tables():
    tables = extract_tables(FIXTURE)
    for name in ["Prologue Remarks", "Wondering Remarks", "Fitting Remarks",
                 "Theodora Checking Remarks", "Lucinda Checking Remarks",
                 "Cinderella Checking Remarks"]:
        assert name in tables, f"missing {name}"
    assert tables["Prologue Remarks"][0]["starting"] == "king's health"
    assert tables["Prologue Remarks"][0]["final"] == "heirs"
    assert "fortunate" in tables["Prologue Remarks"][0]["comment"]

def test_prune_only_loops_and_invalid():
    tables = extract_tables(FIXTURE)
    kept, pruned = apply_prune_rules(tables)
    reasons = {p["reason"] for p in pruned}
    assert reasons <= {"loop", "invalid-input"}
    assert any(p["table"] == "Bad Bird Excuses" for p in pruned)

def test_extracts_reactions_topic_response():
    tables = extract_tables(FIXTURE)
    assert "Reactions" in tables, "missing Reactions"
    assert tables["Reactions"][0]["topic"] == '"cracker/polly"'
    assert "Polly wanna cracker" in tables["Reactions"][0]["response"]
    kept, _ = apply_prune_rules(tables)
    assert "Reactions" in kept
