# Phase 2: Extraction - Context

**Gathered:** 2026-03-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Convert mathematical text descriptions into structured algorithm steps. This phase implements the extraction workflow that parses natural language algorithm descriptions and converts them into a machine-readable format that can be used for code generation. User can review and edit extracted steps before proceeding to generation.

**Out of scope:** Multi-algorithm detection, LaTeX/PDF parsing, advanced ambiguity resolution (deferred to v2)

</domain>

<decisions>
## Implementation Decisions

### Parsing Approach
- **D-01:** Hybrid extraction: Rule-based pre-processing + LLM-based structured extraction
- **D-02:** Rule-based layer handles: mathematical notation normalization, section identification, basic structure detection
- **D-03:** LLM layer handles: semantic understanding, step sequencing, implicit variable detection
- **D-04:** Two-pass extraction: First pass identifies algorithm boundaries, second pass extracts structured steps

### Structured Format
- **D-05:** Internal format: JSON Schema with typed steps (loop, conditional, assignment, return, call)
- **D-06:** Display format: Pseudocode-like representation for user review
- **D-07:** Step types supported:
  - `assignment`: Variable assignment with expression
  - `loop`: For/while loops with condition and body
  - `conditional`: If/else with condition and branches
  - `return`: Return statement with value
  - `call`: Function/procedure calls
  - `comment`: Annotations and explanations
- **D-08:** Each step has: id, type, description, inputs (variables read), outputs (variables written), line numbers from source

### Mathematical Notation
- **D-09:** Common constructs to handle:
  - Summation notation (Σ) → loop with accumulator
  - Product notation (Π) → loop with multiplication
  - Set notation (∈, ⊆) → membership/contains checks
  - Matrix notation → 2D array operations
  - Arrow notation (→) → assignments or mappings
- **D-10:** Mathematical operators: Standard symbols (+, -, ×, ÷, ^, √) mapped to Python equivalents
- **D-11:** Subscripts and superscripts: x_i → x[i], x^2 → x**2

### Algorithm Boundaries
- **D-12:** Single algorithm focus: Assume one algorithm per extraction (multi-algorithm deferred to v2)
- **D-13:** Boundary detection: Look for headers ("Algorithm X", "Procedure Y", "Input/Output" sections)
- **D-14:** Context window: Extract up to 5000 characters around identified algorithm

### Input/Output Detection
- **D-15:** Input detection: Look for "Input:", "Given:", "Parameters:" sections or variable declarations at start
- **D-16:** Output detection: Look for "Output:", "Returns:", "Result:" sections or return statements
- **D-17:** Variable typing: Infer types from context (int, float, array, matrix) not explicit type annotations

### User Review Workflow
- **D-18:** Review interface: Side-by-side view (original text | structured steps)
- **D-19:** Edit capabilities: User can edit step descriptions, reorder steps, delete steps, add steps
- **D-20:** Validation on edit: Ensure edited steps maintain required structure (type, inputs, outputs)
- **D-21:** Save extracted: Structured steps saved to `.algomath/algorithms/{name}/steps.json`
- **D-22:** Proceed gate: User must explicitly approve extracted steps before generation

### Error Handling
- **D-23:** Extraction failures: Categorized as parse_error (syntax), ambiguity_error (unclear structure), incomplete_error (missing info)
- **D-24:** User notification: Clear message explaining what couldn't be extracted with suggestions
- **D-25:** Partial extraction: Extract what can be parsed, mark uncertain steps for review
- **D-26:** Retry mechanism: User can provide clarifying text for ambiguous sections

### Performance
- **D-27:** Timeout: 30 seconds maximum for extraction (prevents hanging on complex text)
- **D-28:** Progress indicators: Show extraction phases (parsing → analyzing → structuring → validating)
- **D-29:** Streaming display: Show steps as they're extracted (not all at once at end)

### the agent's Discretion
- Specific regex patterns for notation detection
- LLM prompt engineering for extraction
- Exact JSON Schema field names and structure
- Error message wording and formatting
- Review UI layout and styling
- Validation rule strictness

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Vision, core value, user profile
- `.planning/REQUIREMENTS.md` — EXT-01 to EXT-06 (Extraction requirements)
- `.planning/ROADMAP.md` — Phase 2 goal and success criteria

### Prior Phase Context
- `.planning/phases/01-foundation/01-CONTEXT.md` — Foundation decisions (D-15 to D-17 on JSON format, D-18 to D-21 on naming)

### Existing Codebase
- `src/workflows/extract.py` — Current extraction stub (run_extraction function)
- `src/intent.py` — Intent detection (IntentType.EXTRACT)
- `.planning/phases/01-foundation/01-01-PLAN.md` — ContextManager and persistence details
- `.planning/phases/01-foundation/01-02-PLAN.md` — Workflow engine patterns

### Research Documents
- `.planning/research/ARCHITECTURE.md` — System components and data flow
- `.planning/research/PITFALLS.md` — Common extraction mistakes to avoid

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Progress indicator**: `show_progress()` in `src/workflows/extract.py` — reuse same format
- **ContextManager**: `.algomath/context.py` — already has `save_text()` and `save_steps()` methods
- **WorkflowState**: `.algomath/state.py` — TEXT_EXTRACTED state exists
- **Intent detection**: `src/intent.py` — EXTRACT intent already defined

### Established Patterns
- Workflow functions accept `ContextManager` as first parameter
- Return dict with 'status', 'progress', 'next_steps' keys
- Use forward references with deferred imports to avoid circular dependencies
- Stubs return placeholder data — Phase 2 will implement actual parsing

### Integration Points
- Extraction workflow connects to ContextManager for persistence
- Extracted steps feed into Generation workflow (Phase 3)
- Progress displayed via same indicator as other workflows (D-09 from Phase 1)
- User review happens before state transitions to STEPS_STRUCTURED

</code_context>

<specifics>
## Specific Ideas

- Extraction should feel like "understanding" the algorithm, not just regex matching
- Steps should read like pseudocode but be precisely structured enough for code generation
- Mathematical notation should be preserved in display format but normalized in internal format
- User should be able to see exactly which part of the original text maps to which step
- Common algorithms (sorting, graph algorithms, numerical methods) should extract reliably
- Ambiguous constructs should be flagged for user clarification, not silently guessed

</specifics>

<deferred>
## Deferred Ideas

- Multi-algorithm detection in single text — v2 requirement EXT-07
- Citation-aware extraction — v2 requirement EXT-08
- Advanced ambiguity resolution with user input — v2 requirement EXT-09
- LaTeX-aware parsing for mathematical symbols — out of scope per PROJECT.md
- PDF document parsing — out of scope per PROJECT.md
- Automatic algorithm categorization — future enhancement

</deferred>

---

*Phase: 02-extraction*
*Context gathered: 2026-03-30*
