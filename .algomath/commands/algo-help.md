---
name: algo-help
description: Show help and available commands
---

# /algo-help

Display the complete AlgoMath command reference with descriptions and example usage.

## Usage

```
/algo-help
/algo-help [command]
```

## Arguments

- `command` (optional) — Show detailed help for a specific command

## Examples

```
/algo-help
/algo-help extract
```

## What it does

1. **Load commands** — Retrieves all available AlgoMath commands
2. **Categorize** — Groups commands by workflow phase
3. **Format display** — Presents commands with descriptions
4. **Show examples** — Includes common usage patterns

## Output

```
┌─────────────────────────────────────────────────────────┐
│  AlgoMath: Command Reference                             │
├─────────────────────────────────────────────────────────┤
│  Extract and Generate                                   │
│  ─────────────────────────────────────────────────────  │
│  /algo-extract [name]    Extract algorithm from text   │
│  /algo-generate          Generate code from steps      │
│                                                         │
│  Execute and Verify                                      │
│  ─────────────────────────────────────────────────────  │
│  /algo-run [input]       Execute generated code        │
│  /algo-verify [expected] Check results correctness     │
│                                                         │
│  Information                                              │
│  ─────────────────────────────────────────────────────  │
│  /algo-status            Show current workflow state    │
│  /algo-list              List saved algorithms          │
│  /algo-help              Show this help message       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Quick Start                                             │
│  ─────────────────────────────────────────────────────  │
│  1. Extract:  /algo-extract "Algorithm Name"              │
│  2. Generate: /algo-generate                             │
│  3. Run:      /algo-run                                  │
│  4. Verify:   /algo-verify                               │
│                                                         │
│  Workflow: Extract → Generate → Execute → Verify        │
│                                                         │
│  Full documentation: .algomath/docs/                    │
└─────────────────────────────────────────────────────────┘
```

## Detailed Help Output

```
/algo-help extract

┌─────────────────────────────────────────────────────────┐
│  /algo-extract — Extract algorithm from text              │
├─────────────────────────────────────────────────────────┤
│  Description:                                            │
│  Parses mathematical text and extracts structured       │
│  algorithm steps.                                        │
│                                                         │
│  Usage:                                                  │
│  /algo-extract [name]                                    │
│                                                         │
│  Arguments:                                              │
│  • name (optional) — Algorithm name for saving          │
│                                                         │
│  Example:                                                │
│  /algo-extract "Dijkstra Shortest Path"                  │
│                                                         │
│  See full documentation:                                 │
│  .claude/commands/algo-extract.md                       │
└─────────────────────────────────────────────────────────┘
```

## Command Summary

| Command | Purpose | Arguments |
|---------|---------|-----------|
| `/algo-extract` | Extract algorithm steps from text | `[name]` |
| `/algo-generate` | Generate Python code | None |
| `/algo-run` | Execute generated code | `[input]` |
| `/algo-verify` | Verify execution results | `[expected]` |
| `/algo-status` | Show current state | None |
| `/algo-list` | List saved algorithms | `[--details]` |
| `/algo-help` | Show this help | `[command]` |

## Workflow Diagram

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Extract │───→│ Generate │───→│ Execute  │───→│ Verify   │
│  (text)  │    │  (code)  │    │  (run)   │    │ (check)  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
      ↑                                              │
      └──────────────────────────────────────────────┘
                    (iterate if needed)
```

## Getting Help

- Use `/algo-help [command]` for detailed command information
- Check `/algo-status` to see your current workflow progress
- View saved algorithms with `/algo-list`
- Full documentation in `.algomath/docs/`
