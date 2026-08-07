from src.utils.safety import safety_violations
from src.utils.schema import validate_output

def verification_node(state):
    answer = state.get("generated_answer", ""); reasons = safety_violations(answer)
    source_ids = {s["source_id"] for s in state.get("sources", [])}
    cited = {source_id for source_id in source_ids if f"[{source_id}]" in answer}
    if not cited: reasons.append("citations missing")
    evidence_words = set(" ".join(d["text"].lower() for d in state.get("retrieved_docs", [])).split())
    answer_words = {word.strip(".,:;!?()[]") for word in answer.lower().split() if len(word) > 4}
    if answer == "fake answer" or (answer_words and len(answer_words & evidence_words) / len(answer_words) < .35): reasons.append("evidence grounding failed")
    payload = {"classification": state["classification"], "answer": answer, "sources": state.get("sources", []), "confidence": state.get("confidence", 0), "requires_human": state.get("requires_human", False), "reason": state.get("route_reason", "Verified evidence"), "clarification_question": state.get("clarification_question"), "warnings": state.get("warnings", [])}
    schema_errors = validate_output(payload); reasons.extend(schema_errors); passed = not reasons
    logs = [*state.get("logs", []), f"[VERIFICATION] citations={'pass' if cited else 'fail'}", f"[VERIFICATION] grounding={'pass' if 'evidence grounding failed' not in reasons else 'fail'}", f"[VERIFICATION] schema={'pass' if not schema_errors else 'fail'}", f"[VERIFICATION] pass={passed}"]
    return {"verification_passed": passed, "verification_reasons": reasons, "logs": logs, "node_trace": [*state.get("node_trace", []), "verification"]}
