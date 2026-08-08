# OrbitDesk Project Specification

## 1. Purpose

Build a fully local support-agent network for fictional OrbitDesk. The system must answer only from supplied OrbitDesk documentation and resolved cases, expose its orchestration decisions, and fail safely when evidence or verification is insufficient.

## 2. Normative source order

The assignment PDF has highest authority. Current KB documents override resolved cases. `data/output_schema.json` defines the final JSON contract. Engineering specification and roadmap guide implementation but may not override the assignment, KB, or schema.

## 3. Functional contract

Input: one user question string.

Output: human-readable answer plus JSON containing `classification`, `answer`, `sources`, `confidence`, `requires_human`, and `reason`; optional schema fields are `clarification_question` and `warnings`.

Classifications: `answerable`, `requires_clarification`, `requires_escalation`, `out_of_scope`, and schema-supported `safe_failure`.

## 4. Graph contract

The graph must use LangGraph and contain these distinct nodes:

1. Triage: deterministic request classification.
2. Retrieval: local embeddings, FAISS search, reranking, evidence selection.
3. Generation: local Hugging Face generation restricted to retrieved evidence.
4. Verification: schema, citation, grounding, and safety checks.
5. Revision: one bounded regeneration using verification failure reasons.
6. Output: human-readable and schema-valid structured response.

Conditional edges send non-answerable triage results directly to output. Verification sends a failed first attempt to revision and a failed second attempt to safe failure. There must be no infinite loop.

## 5. State contract

`AgentState` is a `TypedDict` carrying query, classification, retrieved documents, candidates, sources, answer, confidence, verification result/reasons, retry count, human requirement, clarification question, warnings, route reason, logs, node trace, model info, test override, and final output. Nodes communicate through state updates, not hidden global data.

## 6. Knowledge contract

Current Markdown KB files are parsed from frontmatter and chunked at approximately 350 words. Resolved cases are read from the top-level `cases` array. Cases with `status: superseded` are excluded. Case material is historical/supporting evidence only. Every selected chunk retains source ID, title, document type, status, and chunk ID internally.

## 7. Model contract

Embedding model: `BAAI/bge-small-en-v1.5`, local cache only. Default generator: `Qwen/Qwen2.5-0.5B-Instruct`, local cache only, selected for CPU feasibility. Larger `Qwen/Qwen2.5-3B-Instruct` runs are supported by `ORBITDESK_LLM_MODEL`. Exact commit SHA and hardware must be recorded after the final live run. No hosted language-model APIs are allowed.

## 8. Safety contract

The assistant may explain documented product behavior and authorized-user procedures. It may not issue refunds, cancel subscriptions, change roles/settings, execute exports or refreshes, contact external providers, reveal/create secrets, inspect accounts, provide legal/medical/financial advice, or request passwords, tokens, cookies, card numbers, or exported customer data.

## 9. Verification contract

The verifier rejects absent citations, source IDs not matching retrieved evidence, low evidence overlap, schema errors, unsafe terms/actions, and the injected `fake answer`. It records check-level logs and failure reasons. The final output is validated against the supplied JSON schema, including strict source properties.

## 10. Required acceptance tests

The implementation must demonstrate direct answer, two-document answer, clarification, out-of-scope request, escalation, and intentionally failed verification followed by one revision and a second verification. Tests must assert graph behavior/routing rather than exact model wording.

## 11. Operational metrics

The system records embedding load time, generation load time, generation mode/model/revision, and question latency. A final submission must include exact model revisions and the hardware used for the live run.

## 12. Non-goals

No hosted API integration, production authentication, deployment infrastructure, managed vector database, account mutation, or fine-tuning is required. The KB is used through RAG at query time; it is not used to train the base model.
