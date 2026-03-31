---
description: "Show current algorithm state and progress"
argument-hint: "[--verbose]"
tools:
  read: true
  write: false
---

<objective>
Display current algorithm state, progress, and available next steps.
Shows workflow state, completion status, and suggestions.
</objective>

<execution>
Check status by running:
```bash
npx algomath-extract algostatus "$@"
```

Or if algomath-extract is installed globally:
```bash
algostatus "$@"
```

This will:
1. Load current algorithm state
2. Display progress and completion status
3. Show available next steps
</execution>

<process>
Display status:

1. **Load Current State**
   - Read context manager state
   - Get current algorithm name
   - Get workflow state

2. **Display Progress**
   - State: IDLE → EXTRACTED → STEPS → CODE → EXECUTED → VERIFIED
   - Show completion percentage
   - Visual progress bar

3. **Show Algorithm Info**
   - Name
   - Step count (if extracted)
   - Code generated (yes/no)
   - Executed (yes/no)
   - Verified (yes/no)

4. **Show Data Status**
   - Source text present
   - Steps structured
   - Code generated
   - Results captured

5. **Suggest Next Steps**
   Based on current state:
   - IDLE: /algo-extract
   - EXTRACTED: /algo-generate
   - CODE_GENERATED: /algo-run
   - EXECUTION_COMPLETE: /algo-verify
   - VERIFIED: Done! /algo-extract for new

6. **Display in Verbose Mode (if --verbose)**
   - Full algorithm details
   - Step list
   - File paths
   - Timestamps
</process>

<examples>

**Show status:**
/algo-status

**Verbose status:**
/algo-status --verbose

</examples>

<next_steps>
Depends on current state - displayed dynamically
</next_steps>
