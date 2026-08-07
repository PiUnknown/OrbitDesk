from src.graph import run_query

def test_direct_answer(): assert run_query("Can a Viewer create API credentials?")["classification"] == "answerable"
def test_clarification(): assert run_query("Sync isn't working")["classification"] == "requires_clarification"
def test_out_of_scope(): assert run_query("Issue a refund")["classification"] == "out_of_scope"
def test_escalation(): assert run_query("Two consecutive render_failed exports")["classification"] == "requires_escalation"
