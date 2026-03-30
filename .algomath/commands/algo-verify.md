---
name: algo-verify
description: Verify execution results and explain algorithm behavior
---

# /algo-verify

Verify the correctness of execution results and provide explanations of algorithm behavior. This command validates that the output matches expected behavior based on the algorithm specification.

## Usage

```
/algo-verify [expected]
```

## Arguments

- `expected` (optional) — Expected output for validation. Can be:
  - Direct value: `/algo-verify 42`
  - JSON: `/algo-verify {"result": [1, 2, 3]}`
  - File path: `/algo-verify @expected_output.json`
  - If omitted, provides analysis without explicit validation

## Examples

```
/algo-verify
/algo-verify {"shortest_path": [0, 1, 2], "distance": 5}
/algo-verify @test_cases/dijkstra_expected.json
```

## What it does

1. **Load results** — Retrieves execution output from context
2. **Analyze behavior** — Reviews what the algorithm computed
3. **Validate correctness** — Compares against expected results (if provided)
4. **Explain steps** — Breaks down how the algorithm arrived at the result
5. **Check edge cases** — Identifies potential edge case issues
6. **Generate report** — Creates verification summary with findings
7. **Show progress** — Displays verification progress with visual indicator
8. **Suggest next steps** — Recommends: fix issues, run more tests, save algorithm, or start new

## Output

```
┌─────────────────────────────────────────────────────────┐
│  AlgoMath: Verification Complete                         │
├─────────────────────────────────────────────────────────┤
│  Algorithm: Dijkstra Shortest Path                      │
│  Progress: Verify: ██████████████ 100% ✓                │
│                                                         │
│  ✓ Execution completed successfully                      │
│  ✓ Output format is valid                              │
│  ✓ Results are mathematically consistent                 │
│                                                         │
│  Analysis:                                              │
│  The algorithm correctly computed shortest paths from    │
│  the source node. All reachable nodes have finite       │
│  distances, unreachable nodes marked as infinity (∞).    │
│                                                         │
│  Execution trace:                                       │
│  1. Initialized distances: [0, ∞, ∞, ∞]                │
│  2. Processed node 0, updated neighbors               │
│  3. Processed node 1, found shorter path to node 2      │
│  4. Completed: all reachable nodes processed            │
│                                                         │
│  Next steps:                                            │
│  1. /algo-list — Save and view all algorithms            │
│  2. /algo-extract — Start a new algorithm                │
│  3. /algo-status — Review current state                  │
└─────────────────────────────────────────────────────────┘
```

## Requirements

- Code must have been executed (use `/algo-run`)
- Execution results must be available in context

## Related Commands

- `/algo-run` — Execute code before verifying
- `/algo-extract` — Start working on a new algorithm
- `/algo-list` — View all saved algorithms
- `/algo-status` — Show current algorithm state
