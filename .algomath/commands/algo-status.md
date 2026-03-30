---
name: algo-status
description: Show current algorithm state and progress
---

# /algo-status

Display the current state of the algorithm workflow, including progress through extraction, generation, execution, and verification phases.

## Usage

```
/algo-status
```

## Arguments

None.

## Examples

```
/algo-status
```

## What it does

1. **Load session** — Retrieves current algorithm session data
2. **Check completion** — Determines which phases are complete
3. **Calculate progress** — Computes overall completion percentage
4. **Show pipeline** — Displays visual workflow state indicator
5. **List available actions** — Shows what commands are currently applicable
6. **Display summary** — Presents algorithm name, current step, and data status

## Output

```
┌─────────────────────────────────────────────────────────┐
│  AlgoMath: Current Status                                │
├─────────────────────────────────────────────────────────┤
│  Session: Dijkstra Shortest Path                        │
│  Started: 2025-03-29 14:22                             │
│                                                         │
│  Workflow Progress:                                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │ [Extract]  →  [Generate]  →  [Execute]  → [Verify]│   │
│  │    ✓            ✓            ○            ○      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Overall: ████████████░░ 50%                            │
│                                                         │
│  Completed:                                             │
│  ✓ Text extracted (156 lines)                          │
│  ✓ Steps structured (12 algorithm steps)               │
│                                                         │
│  In Progress:                                           │
│  ○ Code generation                                      │
│                                                         │
│  Next actions:                                          │
│  → /algo-generate — Generate Python code                 │
│  → /algo-extract — Extract different algorithm           │
│                                                         │
│  Data Summary:                                          │
│  Algorithm name: Dijkstra Shortest Path                │
│  Saved to: .algomath/algorithms/dijkstra/              │
│  Last modified: 2025-03-29 14:25                       │
└─────────────────────────────────────────────────────────┘
```

## Progress States

- **✓ Complete** — Phase finished, data available
- **○ In Progress** — Phase can be started or resumed
- **— Blocked** — Prerequisites not met

## Related Commands

- `/algo-extract` — Start extraction phase
- `/algo-generate` — Start generation phase
- `/algo-run` — Start execution phase
- `/algo-verify` — Start verification phase
- `/algo-list` — View all saved algorithms
