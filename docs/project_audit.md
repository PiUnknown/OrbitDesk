# Project Audit - 2026-08-07

## Source review

Reviewed in priority order: `assignment.pdf`, all ten KB documents, `data/output_schema.json`, `data/resolved_cases.json`, `engineering_spec.md`, and `roadmap.md`. The assignment requires a local Hugging Face generation model, graph routing, evidence-only answers, verification/revision, logs, five scenarios, model revisions/timing, a graph image, and video-ready traces. The supplied schema additionally permits `safe_failure` and forbids extra final-output fields.

## Completed requirements

- LangGraph is declared and a six-node graph skeleton exists.
- A TypedDict state, conditional triage and verification edges, bounded retry counter, local embedding adapter, FAISS adapter, CLI trace, and basic route tests exist.
- No hosted LLM client is present.

## Gaps and remediation plan

| Area | Gap / why it matters | Requirement | Concrete plan |
|---|---|---|---|
| Assignment coverage | No evidence of an actual local response-generation model, exact revisions, hardware run record, graph PNG, or sample outputs. Reviewers cannot verify core claims. | Assignment: Local Model Requirements; Submission | Implement a Transformers Qwen adapter, model manifest/timing, graph renderer, sample-run output, and README instructions. |
| Graph behavior | Only `answerable` reaches retrieval; safe failure is absent; revision path cannot be injected end-to-end. | Assignment: conditional routing and fallback; schema | Add `safe_failure`, explicit graph routes, and an `initial_answer_override` test seam that visibly traverses verify-revise-verify. |
| Shared state | State lacks evidence chunks, routes, model/timing data, schema errors, and a structured final contract. | Assignment: shared typed state; engineering state design | Expand typed state and make each node append only state updates/logs. |
| Routing | Keyword triage misses documented escalation triggers, privacy events, unclear object/symptom cases, and mislabels any sentence containing `legal`. | KB-006, KB-008, KB-010 | Implement deterministic ordered rules tied to documented conditions, with reasons recorded. |
| Retrieval | Ingest expects a JSON list but the supplied cases use a top-level `cases` object; it ignores `document_id`; it does not chunk; and it can index superseded guidance. | Assignment: supplied docs/cases; KB-001/005; codex instructions | Parse frontmatter and case arrays, 350-word chunks, retain metadata, exclude superseded cases, retrieve five then rerank/select three. |
| Attribution | Final source objects contain `document_type`, violating schema `additionalProperties: false`; citations have malformed spacing; no passage provenance. | output_schema.json; Assignment verification | Keep internal metadata separately; final sources use exactly `source_id` and `passage`, while answer citations use `[KB-###]`. |
| Generation | Current generator concatenates raw document text and is not a Hugging Face LLM; it has no evidence prompt or answer length control. | Assignment: local generation, evidence-only | Add a locally cached Transformers causal-LM adapter with strict prompt and test-only deterministic composer. |
| Verification | Handwritten checks do not load/validate the supplied schema, do not detect unsupported actions comprehensively, and grounding check is brittle. | Assignment Verification; KB-010 | Use `jsonschema`, citation/source consistency, safety patterns, and token-overlap grounding; retain individual check outcomes. |
| Safety | Secrets, account-action claims, medical/financial advice, prompt injection, billing/ownership, and escalation collection are incomplete. | KB-008 and KB-010 | Centralize safety rules, constrain prompts, select safe clarification/escalation wording, and never include secrets in source snippets. |
| Retry | Retry limit exists but no graph test proves it, and failure output preserves the original classification rather than schema-valid `safe_failure`. | Assignment Required Test 5; schema | Revision consumes reasons; second failure becomes `safe_failure`; test trace asserts verify->revision->verify. |
| Traceability | Logs do not identify routes, check-level outcomes, model identity/timing, document selection rationale, or source priority decisions. | Assignment Orchestration; codex instructions | Emit structured, terminal-visible logs at every node and include a serializable trace in results. |
| Tests | Missing escalation route; no source/schema/safety tests; no real case ingestion test; revision graph test is only a comment. | Assignment Required Test Cases; roadmap Phase 9 | Add deterministic unit and end-to-end tests for all required paths, schema, KB-over-case, superseded exclusion, and retry bound. |
| Architecture | Services are reconstructed per query; model fallback silently makes the project look local-model-enabled when it is not; README overstates readiness. | Assignment local model / engineering judgment | Inject services into graph construction, make normal mode require cached local models, isolate test composer, and document setup honestly. |

## Prioritized implementation checklist

1. Repair source ingestion, metadata, chunking, and source priority.
2. Expand typed state and deterministic triage/safety rules.
3. Replace generation and verification with local-model/schema-valid implementations.
4. Complete graph routes, bounded revision, output shaping, and structured logs.
5. Add complete automated coverage and run it.
6. Add README, model manifest, graph image/sample outputs, then record environment details after the local model run.
