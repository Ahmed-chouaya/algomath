# Roadmap: AlgoMath

**Created:** 2025-03-29
**Version:** v1.0
**Phases:** 5

## Overview

| # | Phase | Goal | Requirements | Status | Plans |
|---|---|-------|------|--------------|--------|-------|
| 1 | Foundation | Build workflow engine and context management | WFE-01 to WFE-05, CTX-01 to CTX-05 | ○ Planned | 3 |
| 2 | Extraction | Convert mathematical text descriptions into structured algorithm steps | EXT-01 to EXT-06 | ○ Planned | 3 |
| 3 | Generation | Build code generation from structured steps | GEN-01 to GEN-06 | ○ Not Started | — |
| 4 | Execution | Create safe code execution environment | EXE-01 to EXE-06 | ○ Not Started | — |
| 5 | Verification | Implement verification and explanation features | VER-01 to VER-05 | ○ Not Started | — |

## Phase Details

### Phase 1: Foundation

**Goal:** Build the core infrastructure that enables all other workflows

**Requirements:**
- WFE-01: Natural language command invocation
- WFE-02: Intent detection and routing
- WFE-03: Context maintenance across workflows
- WFE-04: Workflow interruption and resumption
- WFE-05: Progress indicators
- CTX-01: Persist extracted algorithms
- CTX-02: Persist generated code
- CTX-03: Persist execution history
- CTX-04: View algorithm history
- CTX-05: Git versioning

**Success Criteria:**
1. User can invoke "extract", "generate", "run", "verify" commands
2. System correctly routes to appropriate workflow
3. Context persists when switching between workflows
4. User can interrupt and resume without data loss
5. Clear visual feedback on workflow progress
6. All state persisted to files and version controlled

**Dependencies:** None (foundation)

**Plans:** 3 plans in 2 waves

| Wave | Plans | Objective |
|------|-------|-----------|
| 1 | 01, 02 | Context Manager persistence; Command and workflow engine |
| 2 | 03 | Comprehensive test suite |

Plan list:
- [x] 01-01-PLAN.md — Context Manager and State Persistence
- [x] 01-02-PLAN.md — Workflow Engine and Command Interface  
- [x] 01-03-PLAN.md — Test Suite and Verification Infrastructure

---

### Phase 2: Extraction

**Goal:** Convert mathematical text descriptions into structured algorithm steps

**Requirements:**
- EXT-01: Input mathematical text
- EXT-02: Identify algorithm boundaries
- EXT-03: Extract inputs/outputs
- EXT-04: Parse into structured steps
- EXT-05: Handle common notation
- EXT-06: User review/edit capability

**Success Criteria:**
1. User can paste algorithm description
2. System extracts clear step-by-step structure
3. Inputs and outputs are correctly identified
4. Common mathematical constructs parsed (loops, conditionals)
5. User can review and correct extraction before proceeding
6. Extraction stored in structured format (JSON/Markdown)

**Dependencies:** Phase 1 (Context management, workflow engine)

**Plans:** 3 plans in 3 waves

| Wave | Plans | Objective |
|------|-------|-----------|
| 1 | 01 | Rule-based extraction: schema types, notation normalization, parser |
| 2 | 02 | LLM extraction, prompts, review interface, workflow integration |
| 3 | 03 | Error handling, validation, persistence integration, comprehensive tests |

Plan list:
- [x] 02-01-PLAN.md — Rule-based extraction: schema, notation, parser, tests
- [x] 02-02-PLAN.md — LLM extraction, prompts, review interface, workflow integration
- [x] 02-03-PLAN.md — Error handling, validation, persistence, end-to-end tests

---

### Phase 3: Generation

**Goal:** Generate executable Python code from structured algorithm steps

**Requirements:**
- GEN-01: Generate Python code
- GEN-02: Include type hints
- GEN-03: Include docstrings
- GEN-04: Syntactically correct code
- GEN-05: Handle mathematical operations
- GEN-06: User review before execution

**Success Criteria:**
1. System generates runnable Python code from extracted steps
2. Code includes clear type hints for mathematical variables
3. Docstrings explain the algorithm purpose and steps
4. Code passes syntax validation
5. Mathematical operations (arithmetic, vectors, matrices) handled
6. User can review and edit before execution

**Dependencies:** Phase 2 (Extracted algorithm steps)

---

### Phase 4: Execution

**Goal:** Execute generated code safely and capture results

**Requirements:**
- EXE-01: Sandboxed execution
- EXE-02: Capture stdout/stderr
- EXE-03: Timeout protection
- EXE-04: File system restrictions
- EXE-05: Execution status reporting
- EXE-06: Meaningful error messages

**Success Criteria:**
1. Code runs in isolated environment (no system access)
2. All output captured and displayed
3. Execution terminates after timeout (30s default)
4. No file system access outside working directory
5. Clear success/failure indication
6. Errors explained in terms mathematicians understand

**Dependencies:** Phase 3 (Generated Python code)

---

### Phase 5: Verification

**Goal:** Verify correctness and explain algorithm behavior

**Requirements:**
- VER-01: Verify no errors in execution
- VER-02: Compare against expected results
- VER-03: Explain behavior in natural language
- VER-04: Identify edge cases
- VER-05: Detailed step explanations

**Success Criteria:**
1. System confirms code executed without errors
2. Optional comparison with expected output
3. Clear explanation of what the algorithm did
4. Edge cases identified and flagged
5. User can request explanation of any specific step
6. Verification report saved with execution

**Dependencies:** Phase 4 (Execution results)

---

## Traceability

### Phase 1 Requirements
- WFE-01, WFE-02, WFE-03, WFE-04, WFE-05
- CTX-01, CTX-02, CTX-03, CTX-04, CTX-05

### Phase 2 Requirements
- EXT-01, EXT-02, EXT-03, EXT-04, EXT-05, EXT-06

### Phase 3 Requirements
- GEN-01, GEN-02, GEN-03, GEN-04, GEN-05, GEN-06

### Phase 4 Requirements
- EXE-01, EXE-02, EXE-03, EXE-04, EXE-05, EXE-06

### Phase 5 Requirements
- VER-01, VER-02, VER-03, VER-04, VER-05

**Total Coverage:**
- v1 requirements: 32
- Mapped: 32
- Coverage: 100% ✓

---

## Constraints & Notes

**Technical Constraints:**
- Python 3.11+ target
- Sandboxed execution required
- Local file-based storage
- Git for versioning

**User Constraints:**
- Target: Mathematicians, not necessarily programmers
- Interface: Natural language via chat
- No LaTeX/PDF parsing (assume text provided)

**Dependencies:**
- Python environment
- AI assistant capabilities
- Git

---

## Phase Order Rationale

The phases build on each other in the natural workflow order:
1. **Foundation** — Must exist for any workflow to function
2. **Extraction** — Input to code generation
3. **Generation** — Input to execution
4. **Execution** — Input to verification
5. **Verification** — Final validation step

Each phase's output feeds the next phase's input.

---

## Risk Mitigation

**Risk:** Extraction accuracy
- **Mitigation:** Phase 2 focus on user review/editing capability
- **Fallback:** Manual step entry if extraction fails

**Risk:** Generated code correctness
- **Mitigation:** Phase 3 focus on verification and review
- **Fallback:** Phase 4 execution will catch runtime errors

**Risk:** Security in execution
- **Mitigation:** Phase 4 sandboxing is critical path item
- **Fallback:** Restrict to trusted algorithms only

---
*Roadmap created: 2025-03-29*
*Next: Run `/gsd-discuss-phase 1` to begin Phase 1 planning*
