# Phase 5: Verification - Context

**Gathered:** 2026-03-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Verify correctness and explain algorithm behavior. This phase takes execution results and provides analysis, explanation, and correctness checking to the mathematician user. 

**Scope:**
- Confirm code executed without errors (VER-01)
- Compare output against expected results if provided (VER-02)
- Explain algorithm behavior in natural language (VER-03)
- Identify potential edge cases (VER-04)
- Support detailed step explanations on request (VER-05)

**Dependencies:** Phase 4 (Execution results available via `ctx.data["results"]`)

**Out of scope:** Formal verification (theorem proving), performance benchmarking, automatic test generation

</domain>

<decisions>
## Implementation Decisions

### Verification Trigger
- **D-01:** Hybrid approach — Quick inline summary shown automatically after execution
- **D-02:** Full verification available via `/algo-verify` command
- **D-03:** Verification can run on both successful and failed executions (diagnostic mode)
- **D-04:** State transition: EXECUTION_COMPLETE → VERIFIED (only on successful verification)

### Explanation Depth
- **D-05:** Always provide brief summary first (1-2 sentences explaining what the algorithm did)
- **D-06:** Offer detailed step-by-step walkthrough on user request
- **D-07:** Walkthrough shows actual values from execution trace when available
- **D-08:** Match explanation style to algorithm complexity (simple algorithms get brief, complex get detailed)

### Expected Results Comparison
- **D-09:** Interactive prompt — After `/algo-verify`, ask: "Do you have expected results to compare?"
- **D-10:** Support both inline value and file input for expected results
- **D-11:** Comparison shows: expected vs actual, with highlight of differences
- **D-12:** Optional feature — user can skip comparison and just get verification

### Edge Case Detection
- **D-13:** Static analysis: Scan code for patterns (empty loops, division by zero potential, recursion depth)
- **D-14:** Execution-based: Run with varied inputs (empty, single element, boundary values)
- **D-15:** Report both detected and potential edge cases
- **D-16:** Edge cases include: empty inputs, single elements, maximum values, negative numbers, zero

### Output Format
- **D-17:** Inline summary first — similar to execution results format
- **D-18:** Structured sections with clear headers: Summary, Execution, Explanation, Edge Cases, Comparison
- **D-19:** Conversational explanations — mathematical reasoning in natural language
- **D-20:** Save full verification report to `.algomath/algorithms/{name}/verification.log`

### Error Explanation
- **D-21:** Primary focus: successful execution verification
- **D-22:** Diagnostic mode: `/algo-verify --diagnostic` for failed executions
- **D-23:** Diagnostic mode explains: where failure occurred, what values were involved, possible mathematical fixes
- **D-24:** Leverage Phase 4 error translation (D-18) but add execution trace context

### Integration Points
- **D-25:** Read execution results from `ctx.data["results"]`
- **D-26:** Read execution log from `.algomath/algorithms/{name}/execution.log`
- **D-27:** Read algorithm steps from `ctx.data["steps"]` for explanation context
- **D-28:** Read generated code from `ctx.data["code"]` for static analysis
- **D-29:** Update help_command to include verification options

### the agent's Discretion
- Exact wording of summary sentences
- Static analysis pattern detection depth
- Edge case test input generation strategy
- Section header formatting and styling
- When to recommend detailed walkthrough vs brief summary
- Diagnostic report detail level

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Vision, core value, user profile (mathematicians, non-technical)
- `.planning/REQUIREMENTS.md` — VER-01 to VER-05 requirements
- `.planning/ROADMAP.md` — Phase 5 goal and success criteria

### Prior Phase Context
- `.planning/phases/04-execution/04-CONTEXT.md` — Execution decisions (D-14 to D-16 on output, D-18 to D-20 on errors)
- `.planning/phases/04-execution/04-01-SUMMARY.md` — ExecutionResult structure, execution log format
- `.planning/phases/04-execution/04-02-SUMMARY.md` — Error translation and display patterns

### Existing Codebase
- `src/cli/commands.py` — Stub `verify_command()` awaiting implementation
- `src/workflows/run.py` — Execution results format
- `src/execution/display.py` — Output formatting patterns
- `src/execution/errors.py` — Error categorization and translation
- `src/extraction/schema.py` — Algorithm structure for explanation context

### Execution References
- `.algomath/context.py` — ContextManager with verification state
- `.algomath/state.py` — WorkflowState (VERIFIED state)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **show_progress()** pattern from Phase 1 — Reuse for verification progress indicators
- **ExecutionFormatter** in `src/execution/display.py` — Reuse formatting patterns
- **ErrorTranslator** in `src/execution/errors.py` — Reuse error categorization
- **verify_command stub** in `src/cli/commands.py` — Starting point for implementation
- **Algorithm dataclass** — Provides step structure for explanation

### Established Patterns
- Workflow functions accept `ContextManager` as first parameter
- Return dict with 'status', 'progress', 'message', 'next_steps'
- Progress indicators use "Phase: ████████░░ 80%" format
- State transitions update ContextManager before returning
- Output saved to `.algomath/algorithms/{name}/` directory
- Progress bar shown during multi-step operations

### Integration Points
- Verification reads execution results from Phase 4
- Results feed into VERIFIED state for workflow completion
- Verification report saved alongside execution log
- COMMAND_MAP in commands.py needs verify_command entry
- State transition: EXECUTION_COMPLETE → VERIFIED

</code_context>

<specifics>
## Specific Ideas

- Verification should feel like a knowledgeable colleague reviewing your work
- Mathematicians should see "what happened" not just "success/failure"
- For expected comparison, highlight matches in green, differences in red
- Edge case warnings should suggest specific test values ("Try n=0, n=1")
- Step-by-step walkthrough should reference original paper notation if available
- Verification report should be saved for later review and citation
- If algorithm had mathematical notation in extraction, verification should use same notation
- Include execution time in verification (mathematicians may care about performance)

</specifics>

<deferred>
## Deferred Ideas

- Formal verification (theorem proving) — v2 or out of scope
- Property-based testing generation — v2 feature
- Complexity analysis (time/space) — v2 (VER-07)
- Automatic test case generation — v2 (GEN-09)
- Performance benchmarking — v2 enhancement
- Integration with proof assistants — out of scope
- Interactive verification debugging — complex, defer

</deferred>

---

*Phase: 05-verification*  
*Context gathered: 2026-03-30*
