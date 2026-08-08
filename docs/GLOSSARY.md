# OrbitDesk Complete Technical Glossary and Walkthrough

This document explains the project from input to final output. It is intentionally more detailed than a conventional glossary so that a new engineer, reviewer, or presenter can understand both what the system does and why it was designed this way.

## 1. One-sentence project definition

OrbitDesk is a local-first, graph-orchestrated RAG support agent: it classifies a question, retrieves authoritative local evidence, asks a locally cached Hugging Face model to write an evidence-constrained response, verifies that response deterministically, revises it at most once when necessary, and returns a safe structured result.

## 2. Exact flow when a user submits input

Suppose the user runs:

```powershell
python main.py "Can a Viewer create API credentials?"
```

### Step 1: CLI input

`main.py` uses Python `argparse` to read the question as a string. It starts a latency timer, calls `run_query(query)`, and prints the resulting human-readable answer, JSON response, trace logs, and elapsed latency.

### Step 2: Initial state

`run_query()` creates a LangGraph application and invokes it with an `AgentState` containing at least:

- `query`: the user question.
- `retry_count`: `0`.
- `logs`: an empty list.
- `warnings`: an empty list.
- `node_trace`: an empty list.
- `initial_answer_override`: normally `None`; tests use it to inject `fake answer`.

This is explicit shared state. Nodes do not pass hidden variables or rely on module-level conversation memory.

### Step 3: Triage

The triage node lowercases the question and applies deterministic product rules. It assigns one route:

- `answerable`: proceed to retrieval.
- `requires_clarification`: ask for missing documented diagnostic fields.
- `requires_escalation`: explain that a documented human-support condition exists.
- `out_of_scope`: refuse unsupported billing, professional-advice, or unrelated actions.

It also writes `requires_human`, an optional `clarification_question`, a route reason, logs, and the `triage` node name. LangGraph then follows a conditional edge based on `classification`.

For an answerable question, the path is `triage -> retrieve`. For the other three initial classifications, the path is `triage -> output`; the system does not retrieve or generate an unnecessary answer for a request that is already known to be unsafe, unclear, or escalation-bound.

### Step 4: Knowledge ingestion and retrieval

The retrieval node reads the project’s `data` directory. It scans every Markdown file under `data/knowledge_base/` and parses frontmatter such as `document_id`, `title`, `status`, and tags. It splits each document into approximately 350-word chunks. Each chunk receives internal metadata:

```text
source_id, title, text, document_type, status, chunk_id
```

It then reads `data/resolved_cases.json`. The file is an object with a `cases` array, not a bare list. Each non-superseded case is converted into searchable text containing its title, symptoms, resolution, important limits, and source-document references. A case is marked `document_type=case`; current documentation is marked `document_type=kb`.

The ingestion rule is important: current KB material is primary truth, while resolved cases are secondary examples. `CASE-0914` is superseded and is not indexed as current guidance.

### Step 5: Embedding

`LocalEmbeddingModel` first attempts to load `BAAI/bge-small-en-v1.5` from the local Hugging Face cache using `local_files_only=True`. The model converts each document chunk and the user query into numeric vectors. Semantically similar text has nearby vector representations.

If a model is unavailable in test mode, the implementation has a deterministic lexical fallback so graph tests can run without downloading hundreds of megabytes. The fallback is not the live assignment demonstration; the live trace must show `model_mode=transformers` for generation and a cached embedding model when available.

### Step 6: FAISS search

The `LocalVectorStore` builds an in-process FAISS inner-product index. It searches the query vector against all chunk vectors and retrieves the top five candidate chunks. No managed vector database or external search service is used.

FAISS is used because it is fast, local, CPU-compatible, easy to inspect, and directly satisfies the assignment’s local retrieval requirement. A small Python similarity fallback exists for environments where FAISS is not installed.

### Step 7: Reranking and evidence selection

The reranker computes deterministic lexical overlap between query terms and candidate text, then keeps up to three chunks. Current KB chunks are sorted ahead of case chunks when they compete. The timezone/export scenario has an explicit dependency safeguard ensuring both `KB-003` and `KB-004` remain selected because the assignment requires that two-document answer.

The node writes:

- `retrieval_candidates`: the top-five candidates.
- `retrieved_docs`: selected evidence chunks with internal metadata.
- `sources`: final-shaped source records containing only `source_id` and `passage`.
- `model_info`: embedding model name and load time.
- retrieval logs and trace entries.

### Step 8: Local generation

The generation node loads a locally cached Hugging Face causal language model through Transformers. The default is `Qwen/Qwen2.5-0.5B-Instruct`, selected because the user’s machine CPU/disk-offloaded the 3B model and made it impractically slow. The 3B model can be selected with `ORBITDESK_LLM_MODEL` on a stronger machine.

The prompt contains only short excerpts from the selected evidence and instructs the model to:

- answer as OrbitDesk Support;
- use only supplied evidence;
- avoid invented steps;
- avoid claiming account access or actions;
- never request secrets;
- cite source IDs;
- be concise.

The model is not trained or fine-tuned on the KB. The project uses RAG: the base model remains general, while retrieved KB passages provide current OrbitDesk facts at request time. This is the correct design because documentation can change and citations must be inspectable.

The node writes `generated_answer`, `confidence`, model name/revision/load timing, generation mode, logs, and trace. If the model omits exact bracket syntax, deterministic code appends the retrieved source IDs. That step preserves provenance; it does not invent facts.

### Step 9: Verification

The verification node treats the model output as untrusted. It runs independent deterministic checks:

1. **Citation check** — at least one cited source ID must match a retrieved source.
2. **Grounding check** — meaningful answer words must overlap retrieved evidence; `fake answer` is explicitly rejected.
3. **Safety check** — reject secret disclosure, unsafe account-action claims, unsupported billing actions, and other protected behavior.
4. **Schema check** — validate the final contract with `data/output_schema.json` and `jsonschema` when installed.
5. **Trace check** — write separate pass/fail logs for citations, grounding, schema, and overall verification.

The supplied schema uses `additionalProperties: false` for source objects, so internal metadata such as `document_type` is intentionally removed before final output. This prevents a technically informative internal record from violating the assignment contract.

### Step 10: Conditional verification route

If verification passes, LangGraph routes to `output`.

If verification fails and `retry_count < 1`, LangGraph routes to `revision`. If verification fails after one revision, it routes directly to output with `safe_failure`. This explicit counter prevents infinite loops.

### Step 11: Revision

The revision node passes the verification reasons to the local generator, increments `retry_count` to one, clears the test-only initial override, and writes a revision log. The revised answer travels through the same verification node again.

The test call `run_query(question, initial_answer_override="fake answer")` demonstrates the exact path:

```text
triage -> retrieval -> generation -> verification(fail)
        -> revision -> verification -> output
```

### Step 12: Output

The output node chooses the final readable answer according to classification:

- clarification: the documented diagnostic question;
- escalation: a human-support instruction;
- out-of-scope: a safe refusal;
- verified answer: the generated answer;
- failed second verification: a safe-failure message.

It creates the final JSON object, validates its shape, appends output logs, and records the `output` trace entry. `main.py` prints both formats.

## 3. Architecture glossary

**Graph orchestration** — A directed workflow where nodes are vertices and conditional edges select the next operation. It makes retries and route decisions inspectable.

**LangGraph** — The orchestration library used to define `START`, `END`, nodes, edges, conditional edges, compilation, and stateful invocation.

**Node** — A focused function that reads state and returns state updates. OrbitDesk has triage, retrieval, generation, verification, revision, and output nodes.

**Conditional edge** — A graph edge selected by a route function. OrbitDesk uses one after triage and one after verification.

**AgentState** — A Python `TypedDict` representing all data shared between nodes. It includes query, classification, evidence, answer, confidence, retry count, safety flags, warnings, logs, trace, and final output.

**Node trace** — Ordered names of nodes that actually executed, useful for review and video demonstrations.

**Retry bound** — Maximum number of revision attempts. OrbitDesk sets this to one.

**Safe failure** — A valid final response that declines to present an unverified answer and asks for human support.

## 4. Retrieval and AI glossary

**RAG (retrieval-augmented generation)** — A pattern that retrieves current source passages and places them in a prompt at answer time. It is not model training.

**Knowledge base (KB)** — The ten supplied current Markdown product documents, IDs KB-001 through KB-010.

**Resolved case** — A historical support record used as secondary evidence. It can illustrate a resolution but cannot override a current KB document.

**Superseded case** — A case explicitly marked historical/obsolete. It must not be presented as current guidance.

**Frontmatter** — Metadata between `---` delimiters at the top of each KB Markdown file.

**Chunk** — A bounded document passage indexed separately to improve retrieval precision and preserve manageable citations.

**Embedding** — A vector representation of text produced by BGE or the test fallback.

**Sentence Transformers** — The Python library used to load the BGE embedding model.

**FAISS** — Facebook AI Similarity Search, used here as an in-process vector index.

**Inner-product search** — The similarity operation used by FAISS after normalized embedding vectors are created.

**Reranker** — A second-stage selector. OrbitDesk uses deterministic token overlap rather than requiring another large model.

**Evidence** — Retrieved chunks considered relevant enough to pass to generation.

**Source attribution** — Keeping a stable source ID and passage attached to the answer. The final schema calls these fields `source_id` and `passage`.

**Grounding** — The relationship between an answer statement and retrieved evidence. Verification rejects answers with insufficient evidence overlap.

**Hallucination** — Unsupported content introduced by the model. The project reduces it with prompt constraints, retrieval, deterministic checks, and bounded revision.

**Hugging Face Transformers** — The local model-loading/generation library used for Qwen.

**Qwen** — The local instruction-tuned causal language model used for response generation. Default: `Qwen/Qwen2.5-0.5B-Instruct`; optional larger override: `Qwen/Qwen2.5-3B-Instruct`.

**Local-only loading** — Model loading with `local_files_only=True`; it prevents runtime network downloads and hosted inference.

**Template mode** — `ORBITDESK_TEMPLATE_MODE=1`, a deterministic fallback used only for fast tests. It is not evidence of the live model requirement.

## 5. Product behavior glossary

**Workspace** — Security/configuration boundary for members, dashboards, connections, and schedules.

**Owner/Admin** — Roles allowed to create or revoke workspace API credentials.

**Analyst** — Can create dashboards, manual exports, and schedules, but cannot create API credentials.

**Viewer** — Read-only role; cannot create API credentials, schedules, connections, or settings.

**API credential** — Workspace server-to-server credential whose secret is shown only once. Support must never request or reproduce the secret.

**Timezone update pending** — Existing recurring schedules keep their saved timezone until the schedule is opened and saved again.

**source_refresh_timeout** — A required connection refresh exceeded the 15-minute wait window.

**destination_unverified** — An export destination must be verified before delivery.

**owner_access_revoked** — The schedule owner no longer has access to the dashboard.

**render_failed** — Rendering failed after data checks; two consecutive occurrences after documented checks trigger escalation.

**connector_internal_error** — Repeated connection failure that can trigger escalation after two failed attempts.

**Run now** — Runs an export manually; it does not change the recurring schedule’s next run.

**Audit log** — Workspace event history stored in UTC and displayed in the viewer’s locale.

## 6. Technology choices and why

**Python** was chosen because it has mature libraries for LangGraph, Hugging Face, FAISS, JSON Schema, and pytest, and is easy to run from a CLI.

**LangGraph** was required by the assignment and makes the conditional verification/revision behavior real rather than a sequence of prompt calls.

**TypedDict** was chosen for visible, lightweight state. Pydantic could provide stronger runtime typing, but the assignment primarily needs inspectable shared state.

**FAISS** was chosen over a managed vector database because the system must operate offline and the dataset is small.

**BGE-small** was chosen as a fast CPU-compatible embedding model. It offers better semantic retrieval than pure keyword matching while remaining much smaller than large instruction models.

**Qwen 0.5B** was chosen after the 3B model’s disk offloading made the user’s machine too slow. The assignment allows small CPU-compatible models and explicitly values engineering trade-offs over model size.

**Deterministic lexical reranking** was chosen to keep the workflow simple, local, testable, and free of another model-load bottleneck. A cross-encoder can be added later.

**JSON Schema** was used because the supplied schema is authoritative and strict. Handwritten validation alone could accidentally accept extra fields.

**pytest** was chosen for route and graph behavior tests. Tests assert classifications and traces rather than fragile exact natural-language wording.

**CLI** was chosen because the assignment explicitly accepts a CLI, and terminal traces make orchestration visible during the video walkthrough without adding frontend complexity.

## 7. Problems encountered and how they were handled

**The starting repository was incomplete.** It did not initially contain usable KB files or a populated case file, so a scaffold was created and later aligned to the actual company materials.

**The real resolved-cases format was an object, not a list.** Ingestion was corrected to read `payload["cases"]` and flatten symptoms, resolution, and limits.

**KB IDs used `document_id`, not `source_id`.** Frontmatter parsing was updated so source attribution uses KB-001 through KB-010 correctly.

**Superseded case guidance could become retrieval evidence.** Superseded cases are now excluded before indexing.

**Internal metadata violated the strict output schema.** Internal chunks retain document type and chunk ID, but final `sources` contain only `source_id` and `passage`.

**The first Transformers pipeline passed `local_files_only` into generation.** Model/tokenizer loading was changed to explicit `AutoTokenizer` and `AutoModelForCausalLM` construction before creating the pipeline.

**The Qwen 3B model was too slow on the user’s machine.** It was disk-offloaded, so the default was changed to Qwen 0.5B and the prompt/output budget was reduced.

**The small model sometimes omitted citations.** A deterministic post-generation attribution step attaches retrieved IDs, while verification still rejects unsupported source IDs.

**A generated answer failed verification because citations were absent.** This demonstrated that verification and safe failure work; the citation normalization then made valid live responses more reliable.

**The original test environment lacked a working Python dependency installation.** A project virtual environment was created, dependencies installed, and all eight tests passed.

**The project has CPU latency.** This is recorded as a hardware limitation rather than hidden. Live runs have shown roughly 30–65 seconds depending on retrieval and model offloading.

## 8. Top priorities during development

1. **Traceability** — A reviewer must see which node ran, why it routed, which documents were retrieved, and whether verification passed.
2. **Source fidelity** — Current KB guidance must beat historical cases, and every generated conclusion needs source attribution.
3. **Safety** — Never expose secrets, pretend to mutate an account, issue refunds, or answer unsupported professional questions.
4. **Deterministic routing** — Security and scope boundaries must not depend only on model judgment.
5. **Verification over trust** — The model output is untrusted until citations, grounding, safety, and schema checks pass.
6. **Bounded execution** — One revision maximum prevents infinite loops and unpredictable cost/latency.
7. **Offline operation** — Runtime model use must work from local caches without hosted APIs.
8. **Hardware awareness** — A smaller model that runs locally is preferable to a larger model that cannot finish in a reasonable time.
9. **Simplicity** — Six clear nodes are better for this assignment than unnecessary multi-agent complexity.
10. **Honest reporting** — Template tests, model limitations, hardware, revisions, and latency must be distinguished clearly.

## 9. What the evaluator should see

The strongest demonstration shows the terminal running an answerable direct question, the timezone/export question retrieving KB-003 and KB-004, a clarification/escalation/refund route, and the fake-answer test path. The presenter should point at `[TRIAGE]`, `[RETRIEVAL]`, `[GENERATION]`, `[VERIFICATION]`, `[REVISION]`, and `[OUTPUT]` logs, then explain that the source IDs come from local retrieval rather than model memory.

## 10. Final handoff commands

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

For presentation, record the model commit SHA, hardware, model-load time, question latency, graph image, sample outputs, and walkthrough link separately. Do not commit `.venv`, model caches, tokens, or secrets.
