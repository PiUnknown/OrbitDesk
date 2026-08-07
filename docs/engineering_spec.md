# OrbitDesk Local-First Support Agent Network

## Engineering Specification for Codex

### Project Goal

Build a fully local AI support agent system for the fictional product OrbitDesk.

The system must answer support questions using only the supplied knowledge base and resolved support cases.

No hosted LLM APIs may be used.

The project must demonstrate:

* Graph-based orchestration
* Shared typed state
* Conditional routing
* Retrieval-Augmented Generation (RAG)
* Verification and retry logic
* Safe handling of unsupported requests
* Full offline operation after model download
* Clear execution traces and logs

This is not a chatbot project.

This is an orchestration and AI systems engineering project.

The evaluator is primarily judging workflow design, reliability, traceability, and engineering decisions.

---

# Success Criteria

A reviewer should be able to see:

1. A real graph-based workflow
2. Clear node separation
3. Typed shared state
4. Local retrieval
5. Local generation
6. Verification layer
7. Retry/revision path
8. Routing decisions
9. Safety controls
10. Structured output

Model quality is secondary.

System correctness is primary.

---

# Required Functional Capabilities

The system must classify requests into:

```text
answerable
requires_clarification
requires_escalation
out_of_scope
```

The system must:

1. Receive a user question
2. Classify intent
3. Retrieve relevant evidence
4. Generate response
5. Verify response
6. Retry once if verification fails
7. Return safe failure if verification still fails

---

# Knowledge Sources

Use only the provided materials:

```text
knowledge_base/*.md
resolved_cases.json
```

Knowledge Base documents are the primary source of truth.

Resolved cases are secondary.

If a resolved case conflicts with the KB:

```text
KB wins
```

Never allow a resolved case to override KB guidance.

---

# High-Level Architecture

```text
                 START
                   |
                   v

            TRIAGE NODE
                   |
      --------------------------------
      |              |              |
      v              v              v

 ANSWERABLE     CLARIFICATION    OUT_OF_SCOPE

      |
      v

        RETRIEVAL NODE
              |
              v

       GENERATION NODE
              |
              v

      VERIFICATION NODE
              |
      ------------------
      |                |
      v                v

    PASS            FAIL
      |                |
      |                v
      |        REVISION NODE
      |                |
      |                v
      |        VERIFICATION NODE
      |                |
      |                |
      |          PASS / FAIL
      |                |
      ------------------
              |
              v

            OUTPUT
```

Maximum revision count:

```text
1
```

Never allow infinite loops.

---

# Technology Stack

## Orchestration

LangGraph

Required because the assignment explicitly asks for graph orchestration.

---

## Embeddings

Preferred:

```text
BAAI/bge-small-en-v1.5
```

Alternative:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Requirements:

* Local
* Fast
* CPU compatible

---

## Vector Search

FAISS

Use local vector indexing.

Do not use external vector databases.

---

## Optional Reranker

Preferred:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

Used after retrieval.

Retrieve Top 5.

Rerank.

Keep Top 3.

---

## Generation Model

Preferred:

```text
Qwen/Qwen2.5-3B-Instruct
```

Quantized if necessary.

Alternative:

```text
microsoft/Phi-3-mini-4k-instruct
```

Generation must run locally.

No OpenAI.

No Anthropic.

No Gemini.

---

# Repository Structure

```text
orbitdesk-agent/

├── data/
│   ├── knowledge_base/
│   ├── resolved_cases.json
│   └── output_schema.json
│
├── src/
│   ├── state.py
│   ├── graph.py
│
│   ├── nodes/
│   │   ├── triage.py
│   │   ├── retrieval.py
│   │   ├── generation.py
│   │   ├── verification.py
│   │   ├── revision.py
│   │   └── output.py
│
│   ├── retrieval/
│   │   ├── ingest.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   └── reranker.py
│
│   ├── models/
│   │   ├── llm.py
│   │   └── embedding_model.py
│
│   └── utils/
│       ├── logging.py
│       ├── schema.py
│       └── safety.py
│
├── tests/
│   ├── test_routing.py
│   ├── test_verification.py
│   └── test_end_to_end.py
│
├── outputs/
│
├── README.md
│
└── main.py
```

---

# Shared State Design

Use TypedDict or Pydantic.

```python
class AgentState(TypedDict):

    query: str

    classification: str

    retrieved_docs: list

    sources: list

    generated_answer: str

    confidence: float

    verification_passed: bool

    retry_count: int

    requires_human: bool

    clarification_question: str | None

    warnings: list[str]

    logs: list[str]
```

Every node reads and writes state.

Never pass data through globals.

---

# Node Specifications

## TRIAGE NODE

Responsibilities:

Classify request.

Possible outputs:

```text
answerable
requires_clarification
requires_escalation
out_of_scope
```

Examples:

### Answerable

```text
Can a Viewer create API credentials?
```

### Clarification

```text
My sync is broken
```

Insufficient information.

### Escalation

```text
Two render_failed exports
```

Known escalation path.

### Out Of Scope

```text
Issue a refund
```

Unsupported action.

---

## RETRIEVAL NODE

Responsibilities:

1. Embed question
2. Search FAISS
3. Retrieve top documents
4. Rerank results
5. Select evidence

Output:

```python
retrieved_docs
sources
```

Store source identifiers.

Never lose source attribution.

---

## GENERATION NODE

Responsibilities:

Generate answer using only retrieved evidence.

Prompt requirements:

```text
You are OrbitDesk Support.

Answer ONLY using supplied evidence.

Do not invent instructions.

Do not assume account access.

Always cite source IDs.

If evidence is insufficient,
say so.
```

Output:

```python
generated_answer
confidence
```

---

## VERIFICATION NODE

Responsibilities:

Validate response quality.

Checks:

### 1. Sources Present

Must contain citations.

### 2. Schema Compliance

Validate against output schema.

### 3. Evidence Grounding

Answer content must be supported.

### 4. Safety

Reject answers that:

* issue refunds
* provide legal advice
* reveal credentials
* expose secrets
* perform unsupported actions

### 5. Hallucination Detection

Answer should not introduce unsupported steps.

---

## REVISION NODE

Activated only when:

```python
verification_passed == False
```

Generate revised answer.

Use verification failure reason.

Increment retry counter.

Maximum retries:

```python
1
```

---

# Retrieval Design

Chunk documents.

Recommended chunk size:

```text
300-500 tokens
```

Metadata:

```python
{
  "source_id": "...",
  "title": "...",
  "document_type": "kb|case"
}
```

Store metadata alongside embeddings.

---

# Logging Requirements

Every node must write logs.

Example:

```text
[TRIAGE]
classification=answerable

[RETRIEVAL]
retrieved=KB-003
retrieved=KB-004

[GENERATION]
tokens=231

[VERIFICATION]
schema=pass
citations=pass
grounding=pass
```

Logs should be visible in terminal output.

---

# Output Contract

Return both:

## Human Readable

```text
Suggested troubleshooting steps...
```

and

## Structured JSON

```json
{
  "classification": "answerable",
  "answer": "...",
  "sources": [
    {
      "source_id": "KB-003",
      "passage": "timezone update pending"
    }
  ],
  "confidence": 0.91,
  "requires_human": false,
  "reason": "Supported by retrieved documentation"
}
```

---

# Required Test Scenarios

Implement exactly these scenarios.

## Test 1

Direct answer.

Example:

```text
Can a Viewer create API credentials?
```

Expected:

```text
answerable
```

---

## Test 2

Multi-document answer.

Example:

```text
Exports stopped after timezone change
```

Must retrieve:

```text
KB-003
KB-004
```

---

## Test 3

Clarification.

Example:

```text
Sync isn't working
```

Expected:

```text
requires_clarification
```

---

## Test 4

Out of scope.

Example:

```text
Issue a refund
```

Expected:

```text
out_of_scope
```

---

## Test 5

Verification failure.

Intentionally inject:

```python
generated_answer = "fake answer"
```

Verification must fail.

Graph must route:

```text
verification
→ revision
→ verification
```

---

# Automated Routing Tests

Do not assert exact wording.

Correct:

```python
assert result["classification"] == "out_of_scope"
```

Incorrect:

```python
assert "refund" in answer
```

Routing tests should verify graph behavior.

---

# Performance Tracking

Record:

## Model Load Time

Example:

```text
Embedding model: 2.1s
LLM model: 8.4s
```

## Response Latency

Example:

```text
Question latency: 1.8s
```

Include in README.

---

# README Requirements

Must include:

1. Project overview
2. Architecture diagram
3. Model names
4. Model revisions
5. Hardware used
6. Setup instructions
7. Example outputs
8. Test instructions
9. Known limitations
10. Future improvements
11. AI-assisted development disclosure

---

# Engineering Principles

Prioritize:

1. Deterministic routing over prompt magic
2. Explicit state over hidden state
3. Verification over trust
4. Simplicity over unnecessary agents
5. Traceability over cleverness
6. Reliability over model sophistication

The strongest submission is not the most complex.

The strongest submission is the one whose behavior is easy to inspect, explain, test, and trust.
