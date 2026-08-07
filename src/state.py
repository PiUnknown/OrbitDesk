from __future__ import annotations
from typing import TypedDict

class Source(TypedDict):
    source_id: str
    passage: str

class AgentState(TypedDict, total=False):
    query: str
    classification: str
    retrieved_docs: list[dict]
    retrieval_candidates: list[dict]
    sources: list[Source]
    generated_answer: str
    confidence: float
    verification_passed: bool
    verification_reasons: list[str]
    retry_count: int
    requires_human: bool
    clarification_question: str | None
    warnings: list[str]
    logs: list[str]
    route_reason: str
    node_trace: list[str]
    model_info: dict
    initial_answer_override: str | None
    final_output: dict
