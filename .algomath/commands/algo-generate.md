---
name: algo-generate
description: Generate executable code from algorithm steps
---

# /algo-generate

Generate executable Python code from structured algorithm steps. This command transforms the extracted algorithm into working, runnable code.

## Usage

```
/algo-generate
```

## Arguments

None. Uses algorithm steps currently stored in context.

## Examples

```
/algo-generate
```

## What it does

1. **Validate input** — Checks if extracted steps exist in context
2. **Analyze structure** — Reviews the algorithm steps for complexity and dependencies
3. **Generate code** — Creates Python implementation matching the algorithm structure
4. **Add documentation** — Includes docstrings and comments explaining the implementation
5. **Type hints** — Adds appropriate type annotations where applicable
6. **Save to context** — Stores generated code for execution phase
7. **Show progress** — Displays generation progress with visual indicator
8. **Suggest next steps** — Recommends: run the code, verify the implementation, or regenerate

## Output

```
┌─────────────────────────────────────────────────────────┐
│  AlgoMath: Generation Complete                          │
├─────────────────────────────────────────────────────────┤
│  Algorithm: Dijkstra Shortest Path                      │
│  Progress: Generate: ████████████░░ 80%                 │
│                                                         │
│  Generated: src/generated/dijkstra.py                   │
│  Lines of code: 45                                      │
│  Functions: 2                                           │
│                                                         │
│  Next steps:                                            │
│  1. /algo-run — Execute the generated code               │
│  2. /algo-verify — Review before running                 │
│  3. /algo-status — Check current state                   │
└─────────────────────────────────────────────────────────┘
```

## Requirements

- Algorithm steps must be extracted first (use `/algo-extract`)
- Steps must be in valid structured format

## Related Commands

- `/algo-extract` — Extract algorithm steps from text
- `/algo-run` — Execute the generated code
- `/algo-verify` — Review and verify the implementation
- `/algo-status` — Show current algorithm state
