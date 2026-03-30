---
name: algo-list
description: List all saved algorithms
---

# /algo-list

Display all saved algorithms with their current status, last modified date, and workflow completion level.

## Usage

```
/algo-list [--details]
```

## Arguments

- `--details` (optional) — Show additional details including file sizes and step counts

## Examples

```
/algo-list
/algo-list --details
```

## What it does

1. **Scan storage** — Reads `.algomath/algorithms/` directory
2. **Load metadata** — Retrieves algorithm names and timestamps
3. **Calculate progress** — Determines completion level for each algorithm
4. **Sort results** — Orders by last modified (most recent first)
5. **Format output** — Displays table with status indicators

## Output

```
┌─────────────────────────────────────────────────────────┐
│  AlgoMath: Saved Algorithms                              │
├─────────────────────────────────────────────────────────┤
│  Total: 3 algorithms                                    │
│                                                         │
│  Name                    Modified    Progress    Status  │
│  ─────────────────────────────────────────────────────  │
│  Dijkstra Shortest Path  Today       ████░░░░░░  Active │
│  Quick Sort              Yesterday   ████████░░ Complete│
│  Matrix Factorization    2 days ago  █░░░░░░░░░  New   │
│                                                         │
│  Legend:                                                │
│  ████░░░░░ = Extraction complete                        │
│  ████████░░ = Code generated                            │
│  ██████████ = Verified                                  │
│                                                         │
│  Next steps:                                            │
│  → /algo-extract [name] — Load existing algorithm        │
│  → /algo-extract — Create new algorithm                  │
└─────────────────────────────────────────────────────────┘
```

## Output with --details

```
┌─────────────────────────────────────────────────────────┐
│  AlgoMath: Saved Algorithms (Detailed)                   │
├─────────────────────────────────────────────────────────┤
│  Dijkstra Shortest Path                                  │
│  ├── Created: 2025-03-28                                │
│  ├── Modified: 2025-03-29 14:25                          │
│  ├── Steps: 12                                          │
│  ├── Code lines: 45                                     │
│  ├── Executions: 3                                       │
│  └── Verified: ✓                                         │
│                                                         │
│  Quick Sort                                              │
│  ├── Created: 2025-03-27                                │
│  ├── Modified: 2025-03-28 09:15                          │
│  ├── Steps: 8                                           │
│  ├── Code lines: 32                                     │
│  ├── Executions: 5                                       │
│  └── Verified: ✓                                         │
└─────────────────────────────────────────────────────────┘
```

## Related Commands

- `/algo-extract [name]` — Load an existing algorithm
- `/algo-status` — Check current session status
- `/algo-help` — Show all available commands
