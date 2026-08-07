from langgraph.graph import END, START, StateGraph
from src.state import AgentState
from src.nodes.triage import triage_node
from src.nodes.retrieval import retrieval_node
from src.nodes.generation import generation_node
from src.nodes.verification import verification_node
from src.nodes.revision import revision_node
from src.nodes.output import output_node

def _triage_route(state): return "retrieve" if state["classification"] == "answerable" else "output"
def _verify_route(state): return "output" if state["verification_passed"] else ("revision" if state.get("retry_count", 0) < 1 else "output")

def build_graph():
    graph = StateGraph(AgentState)
    for name, node in [("triage", triage_node), ("retrieve", retrieval_node), ("generate", generation_node), ("verify", verification_node), ("revision", revision_node), ("output", output_node)]: graph.add_node(name, node)
    graph.add_edge(START, "triage")
    graph.add_conditional_edges("triage", _triage_route, {"retrieve": "retrieve", "output": "output"})
    graph.add_edge("retrieve", "generate"); graph.add_edge("generate", "verify")
    graph.add_conditional_edges("verify", _verify_route, {"revision": "revision", "output": "output"})
    graph.add_edge("revision", "verify"); graph.add_edge("output", END)
    return graph.compile()

def run_query(query: str, initial_answer_override: str | None = None) -> dict:
    return build_graph().invoke({"query": query, "retry_count": 0, "logs": [], "warnings": [], "node_trace": [], "initial_answer_override": initial_answer_override})
