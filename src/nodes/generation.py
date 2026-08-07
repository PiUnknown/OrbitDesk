from src.models.llm import LocalLLM

def generation_node(state):
    llm = LocalLLM()
    answer = state.get("initial_answer_override") or llm.generate(state["query"], state.get("retrieved_docs", []))
    info = {**state.get("model_info", {}), "generation_model": llm.model_name, "generation_revision": llm.revision, "generation_load_seconds": round(llm.load_seconds, 3), "generation_mode": "transformers" if llm.pipeline else "template_fallback"}
    return {"generated_answer": answer, "confidence": .85 if state.get("retrieved_docs") else .2, "model_info": info, "logs": [*state.get("logs", []), "[GENERATION] evidence_only=true", f"[GENERATION] model_mode={info['generation_mode']}"], "node_trace": [*state.get("node_trace", []), "generation"]}
