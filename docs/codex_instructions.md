# OrbitDesk Support Agent Implementation Instructions

You are implementing the OrbitDesk Local-First Support Agent Network from scratch.

Before writing any code, read and understand ALL project files.

## Required Reading Order

1. Assignment PDF
2. README provided with the assignment
3. All knowledge base markdown files
4. resolved_cases.json
5. output_schema.json
6. engineering_spec.md
7. roadmap.md

Do not start implementation until you have inspected every file.

---

# Source of Truth Priority

When multiple files contain related information, use this priority order:

1. Assignment PDF (highest priority)
2. Knowledge Base documents
3. output_schema.json
4. resolved_cases.json
5. engineering_spec.md
6. roadmap.md
7. Your own implementation choices

If there is any conflict:

* Assignment requirements override everything.
* Knowledge Base documents override resolved cases.
* Current documentation overrides historical examples.
* Do not invent behavior not supported by the provided material.

---

# Project Objective

Build a fully local support agent system for OrbitDesk that:

* Runs without internet access after model download
* Uses local Hugging Face models
* Uses graph-based orchestration
* Uses retrieval over supplied documents
* Generates grounded answers
* Verifies answers before returning them
* Returns both human-readable and structured JSON outputs

The goal is not to build a chatbot.

The goal is to demonstrate:

* AI Engineering
* Agent orchestration
* State management
* Retrieval systems
* Verification and reliability
* Safe response behavior

---

# Knowledge Base Rules

Treat the supplied OrbitDesk documentation as the primary source of truth.

Answers must be grounded in:

* Knowledge Base documents
* Resolved cases

If retrieved evidence is insufficient:

* Ask for clarification
* Return safe failure

Never answer using general world knowledge when the knowledge base does not support the answer.

Never invent product behavior.

Never invent permissions.

Never invent troubleshooting steps.

Never invent escalation procedures.

---

# Resolved Cases Rules

Resolved cases are supporting evidence only.

Use them as examples.

Do not allow a resolved case to override a current KB document.

Cases marked as:

```text id="l5a1u6"
superseded
```

must never be treated as current guidance.

If a superseded case is retrieved:

* Flag it as historical
* Prefer current documentation

---

# Output Schema Rules

Inspect output_schema.json before implementation.

The implementation should validate all final responses against that schema.

If the schema and engineering_spec differ:

Follow the schema.

---

# Engineering Requirements

The final system must demonstrate:

* Shared typed state
* Conditional routing
* Retrieval node
* Generation node
* Verification node
* Retry or revision path
* Logging
* Infinite-loop protection

Do not implement a simple sequential pipeline.

A graph is required.

---

# Architecture Expectations

Use the architecture described in engineering_spec.md unless it violates:

* Assignment requirements
* KB rules
* Output schema requirements

The architecture should remain:

```text id="s6hn6e"
Triage
→ Retrieval
→ Generation
→ Verification
→ Revision (if needed)
→ Output
```

with conditional routing.

---

# Verification Requirements

Verification must check:

1. Schema validity
2. Source references
3. Evidence grounding
4. Unsupported actions
5. Hallucinated instructions

Verification should use deterministic checks whenever possible.

Do not rely solely on an LLM judge.

---

# Safety Requirements

The OrbitDesk documentation contains explicit support boundaries.

The system must respect them.

Never:

* Issue refunds
* Provide legal advice
* Reveal credentials
* Request secrets
* Pretend to perform account actions
* Pretend to inspect a user's account

If documentation indicates an action requires a human team or privileged role:

State that clearly.

---

# Logging Requirements

All graph execution paths should be visible.

Reviewers should be able to see:

* Node execution order
* Routing decisions
* Retrieved documents
* Verification outcomes
* Retry behavior

Logs should help explain why the graph made a decision.

---

# Testing Requirements

Implement all required assignment scenarios.

Include automated tests for:

* answerable
* clarification
* escalation
* out_of_scope
* verification failure

Routing tests should validate graph behavior rather than exact wording.

---

# Code Quality Expectations

Prioritize:

1. Correctness
2. Traceability
3. Simplicity
4. Reliability
5. Maintainability

Do not over-engineer.

Do not create unnecessary agents.

Do not build multi-agent systems unless required.

A simple, clean, well-tested graph is preferred over a complex design.

---

# Before Finalizing

Verify that:

* Every assignment requirement is satisfied
* Every required test case works
* The system functions offline after model download
* Sources are preserved throughout the workflow
* The output schema validates successfully
* Logs clearly show graph execution
* Retry paths can be demonstrated

Build the implementation as if a reviewer will inspect every routing decision and every source used to generate an answer.
