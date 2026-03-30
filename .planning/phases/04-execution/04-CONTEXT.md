# Phase 4: Execution - Context

**Gathered:** 2026-03-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Execute generated Python code safely and capture results. This phase takes the approved Python code from Phase 3 (Generation) and runs it in a sandboxed environment with proper isolation, timeouts, and output capture. Execution happens automatically after user approves generated code, with results displayed inline and persisted for later review.

**Out of scope:** Multi-language execution (v2), distributed execution (v2), GPU acceleration (v2)

</domain>

<decisions>
## Implementation Decisions

### Sandboxing Approach
- **D-01:** Use subprocess-based isolation: Spawn separate Python process for execution
- **D-02:** Resource limits: Apply CPU and memory limits to subprocess
- **D-03:** Process termination: Can force-kill hung processes via subprocess termination
- **D-04:** No container overhead: Avoid Docker for v1 (startup time too slow for algorithm testing)

### Timeout Handling
- **D-05:** Default timeout: 30 seconds for algorithm execution
- **D-06:** Hard termination: Send SIGKILL immediately on timeout (no graceful shutdown)
- **D-07:** Clear status reporting: Return TIMEOUT status with execution summary
- **D-08:** User notification: Explain that algorithm exceeded time limit, suggest checking for infinite loops

### File System Restrictions
- **D-09:** Temp sandbox: Redirect all file operations to a temporary directory
- **D-10:** Auto-cleanup: Delete temp directory immediately after execution completes
- **D-11:** Working directory isolation: Change to temp directory before execution, restore after
- **D-12:** Block system paths: Prevent access to /etc, /usr, etc. outside temp sandbox

### Output Capture and Display
- **D-13:** Dual capture: Save stdout/stderr to files AND display inline during execution
- **D-14:** File persistence: Save outputs to `.algomath/algorithms/{name}/execution.log`
- **D-15:** Inline display: Show output with progress indicators (50 lines max, then summarize)
- **D-16:** Execution metadata: Capture runtime, status, timestamp alongside outputs

### Error Handling Strategy
- **D-17:** Error categorization: Classify into SyntaxError, RuntimeError, TimeoutError, MemoryError
- **D-18:** Translation layer: Convert common errors to mathematician-friendly language:
  - SyntaxError → "Generated code has a syntax issue"
  - TimeoutError → "Algorithm took too long to complete — check for infinite loops"
  - MemoryError → "Algorithm used too much memory"
- **D-19:** Show technical details: Include original Python traceback in collapsed section for debugging
- **D-20:** Contextual hints: Suggest fixes based on error type (e.g., "Check loop conditions for infinite loops")

### Integration with Prior Phases
- **D-21:** Auto-trigger: Execute immediately after user approves generated code in Phase 3
- **D-22:** State transition: Move from CODE_GENERATED → EXECUTING → EXECUTION_COMPLETE
- **D-23:** Progress display: Show "Execute: ████████░░ 80%" during execution (per Phase 1 D-09)
- **D-24:** Execution gate: User can review execution results before proceeding to Phase 5 (Verification)
- **D-25:** Skip option: Allow user to skip execution and proceed directly to verification (for manual testing)

### Execution Environment
- **D-26:** Python version: Use system Python 3.11+ (same as generation target)
- **D-27:** Available libraries: Include numpy, math, typing, random (math-focused standard library)
- **D-28:** Import restrictions: Block imports of os, sys, subprocess, network modules
- **D-29:** Input handling: Support stdin redirection for algorithms requiring input
- **D-30:** Return values: Capture function return values for algorithms that return data

### the agent's Discretion
- Exact subprocess implementation (subprocess.run vs Popen)
- Temp directory path and naming convention
- Specific resource limit values (memory, CPU)
- Output formatting and truncation rules
- Error translation wording and detail level
- Progress indicator update frequency
- Execution log file format and structure

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Vision, core value, user profile
- `.planning/REQUIREMENTS.md` — EXE-01 to EXE-06 (Execution requirements)
- `.planning/ROADMAP.md` — Phase 4 goal and success criteria

### Prior Phase Context
- `.planning/phases/01-foundation/01-CONTEXT.md` — Foundation decisions (progress indicators D-09)
- `.planning/phases/02-extraction/02-CONTEXT.md` — Extraction decisions (Algorithm structure)
- `.planning/phases/03-generation/03-CONTEXT.md` — Generation decisions (D-35 to D-36 on proceed gate, auto-import handling)

### Existing Codebase
- `src/workflows/generate.py` — Generation workflow (entry point for execution)
- `src/workflows/run.py` — Execution workflow stub (to be implemented)
- `src/generation/code_generator.py` — Code structure that will be executed
- `.algomath/state.py` — State machine (add EXECUTING, EXECUTION_COMPLETE states)

### Execution References
- `.planning/phases/03-generation/03-RESEARCH.md` — Research on code safety and sandboxing
- `.planning/research/ARCHITECTURE.md` — System data flow and phase connections

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **show_progress()** in `src/workflows/generate.py` — Reuse for execution progress bars
- **ContextManager** in `.algomath/context.py` — Has `save_execution()` method stub
- **WorkflowState** in `.algomath/state.py` — Has EXECUTING state enum value
- **Algorithm dataclass** in `src/extraction/schema.py` — Provides algorithm name, inputs, outputs

### Established Patterns
- Workflow functions accept `ContextManager` as first parameter
- Return dict with 'status', 'progress', 'next_steps' keys
- Progress indicators use "Phase: ████████░░ 80%" format (from Phase 1 D-09)
- State transitions update ContextManager before returning
- File paths follow `.algomath/algorithms/{name}/` structure

### Integration Points
- Execution workflow connects to generation output (approved Python code)
- Execution results feed into verification phase (Phase 5)
- ContextManager saves execution results to `.algomath/algorithms/{name}/execution.log`
- State transitions: CODE_GENERATED → EXECUTING → EXECUTION_COMPLETE
- Progress displayed via same indicator as other workflows

</code_context>

<specifics>
## Specific Ideas

- Execution should feel immediate after code approval — no extra "Run it?" prompt
- Timeout errors should specifically mention checking loop conditions (common in algorithm translations)
- Include execution time in results — mathematicians may care about performance
- If execution produces large output (>50 lines), show summary + option to view full log
- Preserve execution history across sessions (per CTX-03 requirement)
- Support algorithms that print results vs algorithms that return values
- Execution sandbox should clean up even if process crashes (temp directory cleanup)
- Consider showing a "spinner" or progress indicator while code runs
- Execution failures should offer "Debug" option to view code with line numbers

</specifics>

<deferred>
## Deferred Ideas

- Multi-language execution (JavaScript, C++) — v2 requirement
- GPU acceleration support — v2 requirement
- Distributed/parallel execution — out of scope
- Persistent execution environment (keep process warm) — optimization for v2
- Execution result caching — future enhancement
- Execution profiling and performance metrics — v2 feature
- Interactive debugging during execution — complex, defer
- Jupyter notebook integration — out of scope
- Web-based code execution UI — out of scope

</deferred>

---

*Phase: 04-execution*
*Context gathered: 2026-03-30*
