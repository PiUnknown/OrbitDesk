from src.nodes.verification import verification_node
from src.graph import run_query

def test_fake_answer_fails():
    state = {"classification": "answerable", "generated_answer": "fake answer", "sources": [{"source_id": "KB-001", "passage": "Viewers cannot create API credentials.", "document_type": "kb"}], "confidence": .8, "requires_human": False}
    assert verification_node(state)["verification_passed"] is False

def test_final_sources_match_schema_shape():
    result = run_query("Can a Viewer create API credentials?")
    assert all(set(source) == {"source_id", "passage"} for source in result["final_output"]["sources"])
