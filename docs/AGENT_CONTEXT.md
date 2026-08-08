# OrbitDesk Agent Handoff Context

This file is a complete working brief for any agent continuing the project.

## Mission

Implement and present the OrbitDesk Local-First Support Agent Network. The reviewer values correctness, graph orchestration, traceability, source discipline, safe failure, and engineering judgment more than fluent model prose.

## Read first

Read `docs/assignment.pdf`, then every file in `data/knowledge_base/`, `data/output_schema.json`, `data/resolved_cases.json`, `docs/codex_instructions.md`, `docs/engineering_spec.md`, and `docs/roadmap.md`. The assignment and current KB outrank all implementation preferences.

## Current implementation

`src/graph.py` builds a LangGraph with triage, retrieve, generate, verify, revision, and output nodes. `src/state.py` defines `AgentState`. Retrieval parses all ten supplied KB documents and the real resolved-case object, excludes superseded cases, chunks text, searches FAISS, reranks, and preserves source IDs. Generation loads cached local Hugging Face models. Verification validates the supplied JSON schema, citations, grounding, and safety. Output emits readable text and strict structured JSON.

## Current model decisions

Default generator is `Qwen/Qwen2.5-0.5B-Instruct` because the user’s CPU-only machine disk-offloaded the 3B model and made generation impractically slow. The 3B model remains a supported override through `ORBITDESK_LLM_MODEL`. Embeddings use `BAAI/bge-small-en-v1.5`. Runtime model loading uses `local_files_only=True`; never add a hosted provider.

## Important source rules

- KB documents are current truth.
- Resolved cases are secondary.
- `CASE-0914` is superseded and must not be indexed.
- Never expose secrets or ask the user to paste them.
- Do not claim to inspect or change an account.
- Refunds, subscription cancellation, legal/medical/financial advice, and unrelated questions must not be answered as normal support.
- Current source IDs in the supplied data are KB-001 through KB-010.

## Acceptance behavior

The following must remain true:

- `Can a Viewer create API credentials?` → `answerable`, sources include KB-002/KB-005.
- Timezone/export question → `answerable`, selected sources include KB-003/KB-004.
- `Sync isn't working` → `requires_clarification` and asks for documented diagnostic fields without secrets.
- `Two consecutive render_failed exports` → `requires_escalation`.
- `Issue a refund` → `out_of_scope` and does not pretend to act.
- `run_query(..., initial_answer_override="fake answer")` → verification, revision, verification, output with retry count one.
- Template-mode tests currently pass 8/8.

## How to work safely

Do not rewrite working architecture unnecessarily. Preserve source attribution and strict output shape. Any model-quality change must keep deterministic verification and the retry bound. If a model load fails, expose the underlying error instead of silently claiming a successful live run. Do not commit `.venv`, model cache files, tokens, or secrets.

## Remaining presentation tasks

The core code is complete. The remaining handoff/submission work is to run the real local model on all required scenarios, record model commit SHAs, hardware and latency, save sanitized sample outputs, export a graph PNG/JPG, and record the 4–7 minute walkthrough. CPU/disk offloading and terse 0.5B wording should be documented as limitations.

## Engineering principles

1. Deterministic routing over prompt magic.
2. Explicit state over hidden state.
3. Verification over trust.
4. Traceability over cleverness.
5. Reliability over model sophistication.
6. Simplicity over unnecessary agents.
7. Current documentation over historical anecdotes.
8. Safe failure over unsupported confidence.

## Handoff commands

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
hf download BAAI/bge-small-en-v1.5
hf download Qwen/Qwen2.5-0.5B-Instruct
$env:ORBITDESK_TEMPLATE_MODE = "1"
python -m pytest -q
Remove-Item Env:ORBITDESK_TEMPLATE_MODE -ErrorAction SilentlyContinue
python main.py "Can a Viewer create API credentials?"
```

## Final honesty requirement

Do not say the project used a local model unless the trace shows `model_mode=transformers`. Do not say all assignment deliverables are complete until the graph image, sample outputs, model revision/hardware record, and walkthrough have been produced.
