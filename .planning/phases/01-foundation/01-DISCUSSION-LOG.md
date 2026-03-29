# Phase 1: Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2025-03-29
**Phase:** 01-foundation
**Mode:** discuss
**Areas discussed:** Command Interface, Context Storage, State Management, Progress Indicators, Git Integration, Error Handling, Algorithm Format, Session Persistence

---

## Command Interface

| Option | Description | Selected |
|--------|-------------|----------|
| Slash commands like GSD | /algo-extract, /algo-generate, /algo-run, /algo-verify | ✓ |
| Natural language detection | User says "Extract this algorithm" | |
| Hybrid approach | Both slash commands AND natural language | |

**User's choice:** Slash commands like GSD
**Notes:** User specifically wanted "like GSD but for mathematical algorithms"

### Command Set Selection

| Command | Purpose | Selected |
|---------|---------|----------|
| /algo-extract | Extract algorithm from mathematical text | ✓ |
| /algo-generate | Generate Python code from structured steps | ✓ |
| /algo-run | Execute generated code in sandboxed environment | ✓ |
| /algo-verify | Verify execution results and explain behavior | ✓ |
| /algo-status | Show current workflow state and context | ✓ |
| /algo-list | View list of saved algorithms | ✓ |
| /algo-history | View previous algorithm iterations | ✓ |
| /algo-help | Show available commands and usage | ✓ |

**User's choice:** All of them

### Orchestrator Mode

| Option | Description | Selected |
|--------|-------------|----------|
| Full auto mode | Automatically runs full workflow | |
| Checkpoint mode | Auto-runs with pauses for review | |
| User choice per session | User selects mode at start | ✓ |
| Intent-based | Different commands for different modes | |

**User's choice:** User choice per session
**Notes:** User wants both auto and step-by-step modes

---

## Context Storage

| Option | Description | Selected |
|--------|-------------|----------|
| Markdown with frontmatter | Human-readable, like GSD | |
| JSON files | Structured, machine-readable | |
| Hybrid approach | Markdown for humans, JSON for data | ✓ |

**User's choice:** Hybrid approach
**Notes:** Best of both worlds for mathematicians who need readability and system needs structure

---

## State Management

**User asked:** "what do you recommand?"

**Recommendation provided:** Flexible branching — mathematicians often need to refine steps, test variations, and iterate. Simple linear would be too rigid. Git-based adds complexity for non-technical users.

**Final decision:** Flexible branching state machine
- User can jump between steps
- System tracks completion status
- Each step editable at any point

---

## Progress Indicators

| Option | Description | Selected |
|--------|-------------|----------|
| Stage banners like GSD | ━━━━━━━━━━━━ ALGO ► EXTRACTING | |
| Simple text indicators | [Extracting...] → [Generating...] | |
| Progress bars | Extract: ████████░░ 80% | ✓ |

**User's choice:** Progress bars
**Notes:** Quantitative feedback preferred

---

## Git Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit commits only | User runs /algo-commit | |
| Auto-commit on milestones | System commits at key points | |
| Background versioning | Internal version history, git optional | ✓ |

**User's choice:** Background versioning
**Notes:** User doesn't need to understand git

---

## Error Handling

**User's response:** "the tool will be used on top of opencode so opencode will handle the errors"

**Decision:** Error handling delegated to OpenCode

---

## Algorithm Format

**User asked:** "what do you recommand from those"

**Recommendation provided:** JSON Schema internally for reliability, display as pseudocode for user review. JSON ensures consistent code generation, pseudocode is readable for mathematicians.

**Final decision:**
- Internal format: JSON Schema
- Display format: Readable pseudocode

---

## Session Persistence

**User asked:** "what do you recommand here"

**Recommendation provided:** Named algorithms — mathematicians work on specific algorithms over time (e.g., "Eigenvalue Decomposition"). Need to return, iterate, compare versions. Named gives control while preserving important work.

**Final decision:**
- Named algorithms with optional naming
- Stored in .algomath/algorithms/{name}/
- Browse with /algo-list
- Unnamed algorithms are session-only

---

## the agent's Discretion

**Areas where user confirmed "you decide":**
- Progress bar styling and percentage calculation
- Specific JSON Schema structure for algorithm steps
- File naming conventions within .algomath/
- Error message formatting

---

## Deferred Ideas

**Ideas mentioned that belong in other phases:**
- Multi-algorithm detection — Phase 2
- Advanced ambiguity resolution — Phase 2
- Alternative implementation options — Phase 3
- Property-based testing — Phase 5
- Formal verification hints — Phase 5
- Export as standalone Python package — v2
- Collaborative features — v2
- Cloud synchronization — out of scope

**Scope maintained:** All discussions stayed within Phase 1 scope

---

*Discussion log: 2025-03-29*
*Context file: 01-CONTEXT.md*
