---
name: algo-extract
description: Extract algorithm from mathematical text
---

# /algo-extract

Extract structured algorithm steps from mathematical text descriptions. This command parses natural language algorithm descriptions and converts them into a structured format suitable for code generation.

## Usage

```
/algo-extract [name]
```

## Arguments

- `name` (optional) — Name for the algorithm. If provided, the algorithm will be saved for later access. If omitted, works in session-only mode.

## Examples

```
/algo-extract "Dijkstra Shortest Path"
/algo-extract
```

## What it does

1. **Check current state** — Verifies if algorithm text already exists in context
2. **Prompt for input** — If no text exists, asks user to provide the algorithm description
3. **Parse algorithm** — Analyzes the text to identify steps, loops, conditions, and operations
4. **Structure output** — Converts natural language into structured algorithm format
5. **Save to context** — Stores extracted steps for the next workflow phase
6. **Show progress** — Displays extraction progress with visual indicator
7. **Suggest next steps** — Recommends: generate code, edit extracted steps, or extract another algorithm

## Output

```
┌─────────────────────────────────────────────────────────┐
│  AlgoMath: Extraction Complete                          │
├─────────────────────────────────────────────────────────┤
│  Algorithm: Dijkstra Shortest Path                      │
│  Progress: Extract: ██████████░░ 80%                    │
│                                                         │
│  Steps extracted: 12                                    │
│  - Initialize distances                                 │
│  - Build priority queue                                 │
│  - Process nodes (loop)                                 │
│  - Update neighbors                                     │
│  - Return result                                        │
│                                                         │
│  Next steps:                                            │
│  1. /algo-generate — Create Python code                │
│  2. /algo-status — Review current state                  │
│  3. /algo-extract — Extract another algorithm            │
└─────────────────────────────────────────────────────────┘
```

## Related Commands

- `/algo-generate` — Generate Python code from extracted steps
- `/algo-status` — Show current algorithm state and progress
- `/algo-list` — View all saved algorithms
