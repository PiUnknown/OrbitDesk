from src.models.llm import LocalLLM

def revision_node(state):
    answer = LocalLLM().generate(state["query"], state.get("retrieved_docs", []), "; ".join(state.get("verification_reasons", [])))
    return {"generated_answer": answer, "confidence": .75, "retry_count": state.get("retry_count", 0) + 1, "initial_answer_override": None, "logs": [*state.get("logs", []), "[REVISION] retry=1", "[REVISION] reasons=" + "; ".join(state.get("verification_reasons", []))], "node_trace": [*state.get("node_trace", []), "revision"]}
