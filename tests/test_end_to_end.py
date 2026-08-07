from src.graph import run_query

def test_multi_document_answer():
    result = run_query("Exports stopped after timezone change")
    assert result["classification"] == "answerable"
    assert {x["source_id"] for x in result["sources"]} >= {"KB-003", "KB-004"}

def test_fake_answer_routes_to_revision_once():
    result = run_query("Can a Viewer create API credentials?", initial_answer_override="fake answer")
    assert result["retry_count"] == 1
    assert result["node_trace"].count("verification") == 2
    assert result["node_trace"] == ["triage", "retrieval", "generation", "verification", "revision", "verification", "output"]
