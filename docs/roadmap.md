# OrbitDesk Support Agent Network
## Implementation Roadmap

This roadmap exists to guide implementation of the OrbitDesk Local-First Support Agent Network described in the assignment, engineering specification, and knowledge base.

The goal is to deliver a fully local, graph-based support agent that demonstrates:

- Shared typed state
- Conditional routing
- Retrieval-Augmented Generation (RAG)
- Verification and revision workflows
- Safe response behavior
- Source attribution
- Traceability and logging

---

# Phase 0: Project Setup

## Objective

Create the repository structure and install all required dependencies.

## Deliverables

- Project structure created
- Python environment configured
- Dependencies installed
- Local models selected
- LangGraph configured

## Success Criteria

- Project runs locally
- Dependencies resolve successfully
- Models can be loaded

---

# Phase 1: Knowledge Ingestion

## Objective

Load and index all provided knowledge sources.

## Inputs

- Markdown knowledge-base documents
- resolved_cases.json

## Tasks

- Load all KB files
- Load resolved cases
- Create document metadata
- Chunk documents
- Generate embeddings
- Build FAISS index

## Success Criteria

Queries return relevant documents from the knowledge base.

---

# Phase 2: Shared State and Graph Architecture

## Objective

Implement graph orchestration and shared state.

## Tasks

- Define AgentState
- Create graph skeleton
- Define node interfaces
- Define routing paths

## Required Nodes

- Triage
- Retrieval
- Generation
- Verification
- Revision
- Output

## Success Criteria

Graph executes successfully from start to finish.

---

# Phase 3: Triage and Routing

## Objective

Classify incoming requests and route appropriately.

## Supported Classifications

- answerable
- requires_clarification
- requires_escalation
- out_of_scope

## Tasks

- Implement triage logic
- Implement routing logic
- Add confidence tracking

## Success Criteria

All sample questions are routed correctly.

---

# Phase 4: Retrieval System

## Objective

Retrieve evidence from the knowledge base.

## Tasks

- Embed user query
- Search vector store
- Retrieve top-k results
- Preserve source metadata
- Optional reranking

## Success Criteria

Relevant supporting documents are consistently retrieved.

---

# Phase 5: Response Generation

## Objective

Generate evidence-grounded responses.

## Tasks

- Implement local LLM interface
- Build generation prompt
- Restrict answers to retrieved evidence
- Attach sources

## Success Criteria

Answers are grounded in retrieved documentation.

---

# Phase 6: Verification Layer

## Objective

Validate generated responses before returning them.

## Verification Checks

### Schema Validation
- Validate against output_schema.json

### Source Validation
- Verify sources exist
- Verify citations are preserved

### Grounding Validation
- Ensure answer is supported by evidence

### Safety Validation
- Detect unsupported actions
- Detect hallucinated instructions
- Detect policy violations

## Success Criteria

Unsafe or unsupported responses are rejected.

---

# Phase 7: Revision Workflow

## Objective

Provide a retry path when verification fails.

## Tasks

- Implement revision node
- Pass verification failure reasons
- Regenerate response
- Re-verify response

## Constraints

Maximum retries:

1

No infinite loops.

## Success Criteria

Verification failures trigger revision workflow correctly.

---

# Phase 8: Logging and Traceability

## Objective

Provide visibility into graph execution.

## Tasks

- Log node execution
- Log routing decisions
- Log retrieval results
- Log verification outcomes
- Log retry behavior

## Success Criteria

A reviewer can understand every graph decision.

---

# Phase 9: Testing

## Objective

Validate system correctness.

## Required Tests

### Routing Tests

- answerable
- requires_clarification
- requires_escalation
- out_of_scope

### Verification Tests

- schema validation
- source validation
- safety validation

### Retry Tests

- verification failure
- revision workflow

### End-to-End Tests

- full graph execution

## Success Criteria

All assignment scenarios pass.

---

# Phase 10: Final Submission

## Objective

Prepare the final deliverable.

## Deliverables

- Complete source code
- README
- Architecture diagram
- Setup instructions
- Sample outputs
- Test instructions
- AI usage disclosure

## Final Validation Checklist

- Runs locally
- Uses local models only
- No remote APIs
- Graph orchestration implemented
- Shared state implemented
- Retrieval implemented
- Verification implemented
- Revision path implemented
- Tests passing
- Output schema validated

---

# Engineering Principles

Prioritize:

1. Deterministic routing over prompt engineering
2. Explicit state over hidden state
3. Verification over blind trust
4. Traceability over complexity
5. Reliability over sophistication
6. Simplicity over unnecessary agents

The strongest submission is one that is easy to inspect, explain, test, and trust.