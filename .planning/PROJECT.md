# AlgoMath

## What This Is

AlgoMath is an agentic framework that transforms AI coding assistants into a reliable mathematical problem-solving environment. It sits on top of the coding assistant and controls how tasks are executed through structured workflows, enabling mathematicians to systematically translate algorithms from academic papers into executable implementations.

The system interprets natural language requests from users (e.g., "Extract this algorithm", "Turn it into code", "Run it") and routes them through predefined workflows for extraction, generation, execution, and verification.

## Core Value

Mathematicians can reliably convert complex algorithmic descriptions from academic papers into correct, reproducible, executable code with minimal back-and-forth iterations.

## Requirements

### Validated

- ✓ GSD framework codebase mapped — existing

### Active

- [ ] User can input mathematical text and trigger extraction workflow
- [ ] System can parse algorithm descriptions and extract structured steps
- [ ] User can request code generation from extracted algorithm steps
- [ ] System can generate executable code from structured algorithm steps
- [ ] User can execute generated code and view results
- [ ] System can run code in controlled environment and capture output
- [ ] User can verify correctness of results or request explanations
- [ ] System can explain algorithm steps and verify execution against expected behavior
- [ ] Framework maintains context across workflows (text, steps, code, results)

### Out of Scope

- Direct LaTeX parsing (assume text extraction is handled upstream)
- Multi-language support beyond Python (focus on one reference implementation)
- Visual/mathematical notation rendering (text-based descriptions only)
- Collaborative features (single user workflow)
- Integration with external mathematical computing systems (Wolfram, MATLAB)

## Context

**Problem Domain:**
Mathematicians often work with algorithms described in academic papers and need to turn them into executable implementations. Current AI chat-based approaches are inefficient and unreliable because interactions are unstructured, the AI often misunderstands algorithms, generated code is inconsistent, and users must go through many back-and-forth iterations without clear workflow or reproducibility.

**Core Workflows:**
1. **Extract:** Parse mathematical descriptions and convert to structured steps
2. **Generate:** Create executable code from structured steps
3. **Execute:** Run code to produce results
4. **Verify:** Check correctness and explain results

**User Profile:**
- Primary: Mathematicians who work with academic papers
- Technical level: Non-technical user (the mathematician focuses on math, not managing AI behavior)
- Goal: Reliable translation from paper to working code

**Key Principles:**
- No free-form chat assistant behavior
- All problem-solving follows structured workflows
- Execution is controlled and predictable
- Reduced back-and-forth and ambiguity
- Simple, accessible experience for non-technical users

## Constraints

- **Tech Stack:** Python (primary), Markdown (documentation), JSON (configuration)
- **Target Environment:** AI coding assistants (Claude, Cursor, OpenCode, etc.)
- **Dependencies:** Minimal runtime dependencies (lean on AI assistant capabilities)
- **User Skill:** System must be accessible to mathematicians without technical background

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python as primary language | Dominant in mathematical computing, familiar to target users | — Pending |
| Workflow-based architecture | Ensures reliability and reproducibility | — Pending |
| Natural language intent detection | Makes system accessible to non-technical users | — Pending |
| Context maintenance across workflows | Enables coherent multi-step problem solving | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2025-03-29 after initialization*
