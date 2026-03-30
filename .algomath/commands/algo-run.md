---
name: algo-run
description: Execute generated code and display results
---

# /algo-run

Execute the generated Python code and capture output. This command runs the algorithm implementation in a controlled environment.

## Usage

```
/algo-run [input]
```

## Arguments

- `input` (optional) — Input data for the algorithm. Format depends on algorithm type:
  - Graph algorithms: adjacency list or matrix
  - Sorting algorithms: list of values
  - Numerical algorithms: parameters
  - If omitted, uses default/example inputs

## Examples

```
/algo-run
/algo-run {"graph": [[0,1,4],[1,2,1]], "start": 0}
/algo-run [5, 2, 8, 1, 9]
```

## What it does

1. **Validate code** — Checks if generated code exists and is syntactically valid
2. **Prepare environment** — Sets up execution context with necessary imports
3. **Parse inputs** — Processes provided input data (or uses defaults)
4. **Execute code** — Runs the algorithm in isolated environment
5. **Capture output** — Records stdout, stderr, and return values
6. **Measure performance** — Tracks execution time and memory usage
7. **Save results** — Stores execution output for verification phase
8. **Show progress** — Displays execution progress with visual indicator
9. **Suggest next steps** — Recommends: verify results, run with different inputs, or modify code

## Output

```
┌─────────────────────────────────────────────────────────┐
│  AlgoMath: Execution Complete                            │
├─────────────────────────────────────────────────────────┤
│  Algorithm: Dijkstra Shortest Path                      │
│  Progress: Execute: ████████████░░ 80%                  │
│                                                         │
│  Execution time: 0.023s                                  │
│  Memory used: 2.4 MB                                      │
│                                                         │
│  Output:                                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Shortest distances from node 0:                   │   │
│  │   Node 0: 0                                       │   │
│  │   Node 1: 4                                       │   │
│  │   Node 2: 5                                       │   │
│  │   Node 3: ∞                                       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Next steps:                                            │
│  1. /algo-verify — Validate results correctness          │
│  2. /algo-run — Run with different inputs              │
│  3. /algo-generate — Modify and regenerate               │
└─────────────────────────────────────────────────────────┘
```

## Requirements

- Code must be generated first (use `/algo-generate`)
- Code must pass syntax validation

## Related Commands

- `/algo-generate` — Generate code before running
- `/algo-verify` — Verify execution results
- `/algo-status` — Show current algorithm state
