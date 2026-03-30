# Phase 2: Extraction - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-30
**Phase:** 02-extraction
**Areas discussed:** Parsing Approach, Structured Format, Mathematical Notation, Algorithm Boundaries, Input/Output Detection, User Review Workflow, Error Handling, Performance

---

## Areas Discussed

### Parsing Approach
**Decision:** Hybrid extraction (Rule-based + LLM)
- Rule-based pre-processing for notation normalization
- LLM-based structured extraction for semantic understanding
- Two-pass extraction: boundaries first, then steps

### Structured Format
**Decision:** JSON Schema with typed steps
- Step types: assignment, loop, conditional, return, call, comment
- Each step tracks: id, type, description, inputs, outputs, line numbers
- Display as pseudocode for user review

### Mathematical Notation
**Decision:** Handle common constructs
- Summation/product notation → loops
- Set notation → membership checks
- Matrix notation → 2D arrays
- Arrow notation → assignments
- Subscripts/superscripts → array indexing

### Algorithm Boundaries
**Decision:** Single algorithm focus
- Assume one algorithm per extraction
- Detect boundaries via headers ("Algorithm", "Procedure", "Input/Output")
- 5000 character context window

### Input/Output Detection
**Decision:** Section-based detection
- Look for "Input:", "Given:", "Parameters:" headers
- Look for "Output:", "Returns:", "Result:" headers
- Infer types from context (not explicit annotations)

### User Review Workflow
**Decision:** Required review before proceeding
- Side-by-side view (original | structured)
- Edit: reorder, delete, add, modify steps
- Validation maintains structure integrity
- Explicit approval gate before generation

### Error Handling
**Decision:** Categorized failures with retry
- Parse errors, ambiguity errors, incomplete errors
- Partial extraction with uncertain steps marked
- User can provide clarifying text
- Clear error messages with suggestions

### Performance
**Decision:** Timeouts and streaming
- 30 second extraction timeout
- Phase-based progress indicators
- Display steps as extracted (streaming)

---

## the agent's Discretion Areas

The following areas were left to the agent's discretion during implementation:
- Specific regex patterns for notation detection
- LLM prompt engineering details
- Exact JSON Schema structure
- Error message wording
- Review UI layout specifics
- Validation rule strictness

---

## Deferred Ideas

The following were noted but deferred:
- Multi-algorithm detection → Phase 2 v2
- Citation-aware extraction → Phase 2 v2
- Advanced ambiguity resolution → Phase 2 v2
- LaTeX-aware parsing → Out of scope
- PDF document parsing → Out of scope

---

*Phase: 02-extraction*
*Discussion logged: 2026-03-30*
