from src.utils.schema import validate_output

def output_node(state):
    kind = state["classification"]
    if kind == "requires_clarification": answer, reason = state["clarification_question"], "More diagnostic context is required."
    elif kind == "requires_escalation": answer, reason = "Please escalate this to human OrbitDesk support with both export IDs.", "Known escalation path."
    elif kind == "out_of_scope": answer, reason = "I cannot issue refunds or perform billing actions. Please contact OrbitDesk billing support.", "Unsupported action."
    elif not state.get("verification_passed"): kind, answer, reason = "safe_failure", "I could not verify a safe, evidence-grounded answer. Please contact human support.", "Verification failed after one revision."
    else: answer, reason = state["generated_answer"], "Supported by retrieved documentation."
    final = {"classification": kind, "answer": answer, "sources": state.get("sources", []), "confidence": state.get("confidence", 0), "requires_human": state.get("requires_human", False) or not state.get("verification_passed", True), "reason": reason}
    errors = validate_output(final)
    return {"final_output": final, "logs": [*state.get("logs", []), "[OUTPUT] structured_output=true", f"[OUTPUT] schema={'pass' if not errors else 'fail'}"], "node_trace": [*state.get("node_trace", []), "output"]}
