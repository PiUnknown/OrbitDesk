# OrbitDesk Local-First Support Agent Network

OrbitDesk is a local-first support-agent workflow for the fictional OrbitDesk product. It answers support questions using retrieval-augmented generation (RAG) over the supplied OrbitDesk knowledge base and resolved support cases. It is an orchestration and reliability project—not a general-purpose chatbot.

The system receives a question, classifies it, retrieves evidence when appropriate, generates an evidence-constrained answer with a locally cached Hugging Face model, verifies that answer, revises it at most once if verification fails, and returns both human-readable and structured output.

## What the assignment requires

The assignment requires a graph-based workflow with shared typed state, conditional routing, local Hugging Face models, retrieval over the supplied material, grounded generation, verification, a bounded retry/revision path, visible logs, and at least five demonstrated scenarios. Hosted LLM APIs are prohibited.

The source-of-truth priority is:

1. Assignment PDF
2. Current knowledge-base documents
3. `data/output_schema.json`
4. `data/resolved_cases.json`
5. `docs/engineering_spec.md`
6. `docs/roadmap.md`
7. Implementation preferences

## Architecture

```text
START
  |
  v
TRIAGE
  |-- answerable ------------------------------+
  |                                             v
  |                                        RETRIEVAL
  |                                             |
  |                                             v
  |                                        GENERATION
  |                                             |
  |                                             v
  |                                        VERIFICATION -- pass --> OUTPUT --> END
  |                                             |
  |                                  fail and retry_count < 1
  |                                             v
  |                                        REVISION
  |                                             |
  |                                             +------> VERIFICATION
  |
  |-- clarification ---------------------------> OUTPUT
  |-- escalation ------------------------------> OUTPUT
  |-- out_of_scope ----------------------------> OUTPUT
  |
  +-- failed verification after one revision -> safe_failure -> OUTPUT
```

The implementation is in `src/graph.py`. Nodes are intentionally separated into triage, retrieval, generation, verification, revision, and output modules. `node_trace` and `logs` make routing inspectable.

## Repository map

```text
data/
  knowledge_base/                 Current Markdown product documentation
  resolved_cases.json             Secondary historical/support evidence
  output_schema.json              Required final JSON contract
docs/
  assignment.pdf                  Assignment brief
  codex_instructions.md           Agent/source-priority instructions
  engineering_spec.md             Engineering guidance
  roadmap.md                      Delivery roadmap
  project_audit.md                Completed requirements-gap audit
  PROJECT_SPEC.md                 This project’s implementation specification
  GLOSSARY.md                     Domain and implementation terms
  AGENT_CONTEXT.md                Handoff context for another coding agent
src/
  state.py                        Typed shared graph state
  graph.py                        LangGraph construction and public runner
  nodes/                          Workflow nodes
  retrieval/                      Ingestion, vector search, reranking
  models/                         Local embedding and generation adapters
  utils/                          Safety and schema validation
tests/                             Automated routing, verification, and end-to-end tests
main.py                            CLI entry point
requirements.txt                   Python dependencies
```

## Knowledge and source policy

The KB is the primary source of current product truth. Resolved cases are secondary examples and cannot override current KB guidance. Cases with status `superseded` are not indexed. The current case file is an object containing a `cases` array; the ingestion layer handles that format.

The system must not invent product behavior, permissions, troubleshooting steps, escalation procedures, or account state. It must never ask for passwords, API secrets, OAuth tokens, session cookies, payment-card numbers, or exported customer data.

## Classification and routing

- `answerable`: the question can be answered from the supplied evidence; it follows retrieval, generation, and verification.
- `requires_clarification`: the symptom/object/error information is insufficient; the system asks for documented diagnostic fields.
- `requires_escalation`: a documented escalation condition is present, such as repeated `render_failed`, repeated `connector_internal_error`, or suspected credential exposure.
- `out_of_scope`: the request asks for a refund, subscription cancellation, professional advice, or another unsupported action.
- `safe_failure`: final schema-supported fallback after one generated answer and one revision still fail verification.

Routing is deterministic. The model is not trusted to decide whether a refund, secret request, or escalation boundary is safe.

## Retrieval pipeline

1. Read every Markdown file under `data/knowledge_base/`.
2. Parse `document_id`, title, status, and other frontmatter metadata.
3. Split source text into approximately 350-word chunks.
4. Add non-superseded resolved cases as secondary chunks.
5. Encode documents and the query with local `BAAI/bge-small-en-v1.5` when available.
6. Search a local FAISS inner-product index for five candidates.
7. Apply a deterministic local lexical reranker and retain three evidence chunks.
8. Prefer current KB chunks over case chunks when evidence competes.
9. Preserve source IDs and passages through generation, verification, and output.

## Generation and verification

The default live generator is `Qwen/Qwen2.5-0.5B-Instruct`, selected for CPU practicality. Set `ORBITDESK_LLM_MODEL` to a cached larger model when hardware permits. The adapter loads from the local Hugging Face cache with `local_files_only=True`; there are no OpenAI, Anthropic, Gemini, or other hosted LLM calls.

The prompt tells the model to use only supplied evidence, cite source IDs, avoid invented steps, avoid account claims, and never request secrets. A deterministic post-generation step attaches retrieved source IDs if the small model omits exact citation syntax. This does not add factual content; it preserves retrieval provenance.

Verification checks:

- Required output schema, including strict source-object fields.
- Citation presence and consistency with retrieved sources.
- Lexical evidence grounding.
- Unsafe actions, secret disclosure, account-action claims, and unsupported advice.
- A maximum retry count of one.

After a failed first verification, the revision node receives the failure reasons and regenerates once. If the second verification fails, output classification becomes `safe_failure`.

## Installation

Use a normal project virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Download/cache models once while network access is available:

```powershell
hf download BAAI/bge-small-en-v1.5
hf download Qwen/Qwen2.5-0.5B-Instruct
```

For a larger run, download `Qwen/Qwen2.5-3B-Instruct` and set `ORBITDESK_LLM_MODEL` accordingly. Record the model commit SHA, machine hardware, and timings for the final submission.

## Running the CLI

Normal live-model mode:

```powershell
Remove-Item Env:ORBITDESK_TEMPLATE_MODE -ErrorAction SilentlyContinue
python main.py "Can a Viewer create API credentials?"
```

The CLI prints a readable answer, structured JSON, node trace, and question latency. Example scenarios:

```powershell
python main.py "My scheduled exports stopped after I changed my workspace timezone. What should I check?"
python main.py "Sync isn't working"
python main.py "Two consecutive render_failed exports"
python main.py "Issue a refund"
```

The test-only template mode avoids loading a multi-gigabyte model:

```powershell
$env:ORBITDESK_TEMPLATE_MODE = "1"
python -m pytest -q
```

Template mode is only for fast tests and graph mechanics. It is not the evidence for the assignment’s local-model demonstration.

## Tests

The suite covers:

- Direct answerable routing.
- Clarification routing.
- Escalation routing.
- Out-of-scope routing.
- Multi-document KB-003/KB-004 retrieval.
- Fake-answer verification failure.
- Strict final source shape.
- `verification -> revision -> verification` with exactly one retry.

Expected result in the prepared environment: `8 passed`.

## Output contract

Final JSON follows `data/output_schema.json`. A typical answerable response contains:

```json
{
  "classification": "answerable",
  "answer": "... [KB-002] [KB-005]",
  "sources": [
    {"source_id": "KB-002", "passage": "Relevant excerpt"}
  ],
  "confidence": 0.85,
  "requires_human": false,
  "reason": "Supported by retrieved documentation."
}
```

The final source objects intentionally contain only `source_id` and `passage`, because the supplied schema sets `additionalProperties` to false. Internal retrieval metadata may contain document type and chunk IDs, but those are not leaked into final JSON.

## Assignment submission checklist

- Run all five required scenario categories with the real cached local model.
- Save sanitized sample outputs and screenshots.
- Record model names, exact revisions, CPU/RAM/GPU, model-load time, and question latency.
- Export the graph as a PNG/JPG for the Google Form.
- Record the 4–7 minute walkthrough showing graph responsibilities, three routes, retrieved evidence, traces, and one revision/safe-failure path.
- Do not commit `.venv`, model caches, API keys, tokens, or customer secrets.

## Known limitations

The small local model can produce terse or slightly awkward wording. CPU/disk offloading can make live responses slow; this is a documented hardware trade-off. Deterministic verification and source preservation are prioritized over language quality. The optional cross-encoder reranker and persistent FAISS index are not required for the current submission.

## AI-assisted development disclosure

AI coding assistance was used to implement and audit this project. The graph, state transitions, source-priority rules, safety controls, and tests are explicit in the repository so a reviewer can inspect the engineering decisions.
