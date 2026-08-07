from src.utils.safety import request_is_out_of_scope

def triage_node(state: dict) -> dict:
    query = state["query"].lower()
    if request_is_out_of_scope(query): classification, human, question, reason = "out_of_scope", True, None, "Unsupported billing or professional-advice request (KB-010)."
    elif ("render_failed" in query and ("two" in query or "2" in query or "consecutive" in query)) or ("connector_internal_error" in query and ("two" in query or "repeated" in query)) or "credential exposure" in query: classification, human, question, reason = "requires_escalation", True, None, "Documented escalation condition (KB-008)."
    elif ("sync" in query and len(query.split()) <= 6) or len(query.split()) < 3: classification, human, question, reason = "requires_clarification", False, "Please share the workspace ID, connection name or ID, current state, last successful refresh, and latest error code. Do not share passwords, tokens, or secrets.", "Insufficient connection diagnostics (KB-006)."
    else: classification, human, question, reason = "answerable", False, None, "Documented OrbitDesk question."
    return {"classification": classification, "requires_human": human, "clarification_question": question, "route_reason": reason, "logs": [*state.get("logs", []), "[TRIAGE] classification=" + classification, "[TRIAGE] reason=" + reason], "node_trace": [*state.get("node_trace", []), "triage"]}
