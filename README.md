# OrbitDesk Local-First Support Agent Network

OrbitDesk is a CLI support workflow that answers only from the supplied documentation and resolved cases. It uses LangGraph for explicit orchestration, local Hugging Face models only, FAISS retrieval, deterministic verification, one bounded revision, and a schema-valid JSON response.

## Graph

```text
START -> TRIAGE --answerable--> RETRIEVAL -> GENERATION -> VERIFICATION --pass--> OUTPUT -> END
                 |                                  ^             |
                 |                                  |             +--fail, retry < 1--> REVISION
                 +--clarification/escalation/out-of-scope--------> OUTPUT
                                                          fail after 1 -> SAFE FAILURE -> OUTPUT
```

The terminal trace records every node, route, evidence selection, verification check, and retry. Use the trace during the required video walkthrough. A rendered PNG/JPG can be generated from this diagram for the Google Form upload.

## Models and offline operation

- Embeddings: `BAAI/bge-small-en-v1.5` (revision: record the downloaded commit in your submission)
- Generation: `Qwen/Qwen2.5-3B-Instruct` (revision defaults to `main`; pin the downloaded commit with `ORBITDESK_LLM_REVISION`)
- Vector search: FAISS inner-product search
- Reranking: deterministic local lexical reranker; swap for `cross-encoder/ms-marco-MiniLM-L-6-v2` if desired

Both model adapters load with `local_files_only=True`; no hosted model API is used. Before the live demonstration, download/cache the models once in a trusted environment. The test suite deliberately uses `ORBITDESK_TEMPLATE_MODE=1` so it remains fast and does not require a multi-GB model. This mode is not a substitute for the required local-model live run.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# Download/cache the exact selected Hugging Face models once, then disconnect network.
$env:ORBITDESK_LLM_MODEL = "Qwen/Qwen2.5-3B-Instruct"
$env:ORBITDESK_LLM_REVISION = "<pinned-commit>"
python main.py "Can a Viewer create API credentials?"
```

For tests:

```powershell
$env:ORBITDESK_TEMPLATE_MODE = "1"
python -m pytest -q
```

## Expected output

Each run prints a readable answer, then JSON conforming to `data/output_schema.json`, followed by a trace. Final source records contain only `source_id` and `passage`, as the schema requires. KB chunks are always preferred to cases; cases marked `superseded` are never indexed.

## Demonstration checklist

Run and capture: a Viewer credential question, timezone/export question, ambiguous sync question, two consecutive `render_failed` events, and a refund request. The `initial_answer_override="fake answer"` test visibly exercises `verification -> revision -> verification`.

Record model load time and response latency printed/returned during your final local-model run, plus CPU/RAM/GPU details, in the submission. The supplied environment is intentionally not claimed as the final hardware run.

## Limitations and future work

The currently available environment lacks a runnable Python dependency environment, so final model download and tests must be run after the setup step above. Production improvements: persist the FAISS index, add the local cross-encoder, require a cached model in non-demo mode, and emit a rendered graph image automatically.

## AI-assisted development disclosure

AI coding assistance was used to implement and review this project. The graph, deterministic routing, source rules, safety boundaries, and tests are kept explicit for reviewer inspection.
