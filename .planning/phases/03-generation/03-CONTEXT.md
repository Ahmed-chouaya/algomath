# Phase 3: Generation - Context

**Gathered:** 2026-03-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Generate executable Python code from structured algorithm steps extracted in Phase 2. This phase transforms the machine-readable Algorithm and Step objects into syntactically correct Python code with type hints and docstrings. User can review generated code before proceeding to execution.

**Out of scope:** Multi-language support (v2), optimization suggestions (v2), automatic test case generation (v2)

</domain>

<decisions>
## Implementation Decisions

### Code Generation Strategy
- **D-01:** Hybrid generation: Template-based for predictable patterns + LLM-based for complex logic
- **D-02:** Template layer handles: Standard control flow (loops, conditionals), assignments, function calls
- **D-03:** LLM layer handles: Complex expressions, mathematical formulas, algorithm-specific logic
- **D-04:** Fallback hierarchy: Template → LLM → User prompt for unsupported constructs

### Type Hints
- **D-05:** Type inference from context: Variable names (e.g., "n" → int, "matrix" → List[List[float]])
- **D-06:** Explicit type hints: All function parameters and return values
- **D-07:** Mathematical types: numpy.ndarray for matrices/vectors, List for sequences, float for real numbers
- **D-08:** Optional type annotations: Union[Type, None] for optional parameters

### Docstring Format
- **D-09:** Google-style docstrings: Args, Returns, Raises sections
- **D-10:** Algorithm description: One-line summary + detailed description from algorithm name
- **D-11:** Complexity notation: Include time/space complexity when inferable from steps
- **D-12:** Step references: Link to original step IDs for traceability

### Code Structure
- **D-13:** Single function output: def algorithm_name(inputs) → outputs
- **D-14:** Naming convention: snake_case, descriptive (e.g., "dijkstra_shortest_path")
- **D-15:** Helper functions: Generate internal helpers for repeated patterns
- **D-16:** Import handling: Auto-import numpy, typing, math based on detected types
- **D-17:** Execution guard: Wrap in if __name__ == "__main__": for standalone execution

### Mathematical Operations
- **D-18:** Operator mapping: Σ → sum() or np.sum(), Π → math.prod() or np.prod(), √ → math.sqrt()
- **D-19:** Matrix operations: Use numpy for matrix arithmetic (@ for multiplication)
- **D-20:** Set operations: Use Python sets for ∈, ⊆, ∪, ∩ operations
- **D-21:** Power/exponent: ** operator for exponents, math.pow() for clarity in complex expressions

### Validation Strategy
- **D-22:** Syntax validation: Parse with ast module before saving
- **D-23:** Import validation: Verify all imports can be resolved
- **D-24:** Runtime check: Optional execution in sandbox to verify no NameError
- **D-25:** User review: Side-by-side view (structured steps | generated code)

### Error Handling
- **D-26:** GenerationError hierarchy: SyntaxError, ImportError, UnsupportedConstructError
- **D-27:** Graceful degradation: If LLM fails, fall back to template stubs
- **D-28:** User notification: Clear message showing what failed with line numbers

### Progress Indicators
- **D-29:** Phase display: "Generate: ████████░░ 80%" per Phase 1 D-09
- **D-30:** Step-by-step: Show progress as each code section is generated
- **D-31:** Preview toggle: Show code as it's generated (not all at once)

### User Review Workflow
- **D-32:** Review interface: Side-by-side view (structured steps | generated code)
- **D-33:** Edit capabilities: User can modify generated code before approval
- **D-34:** Validation on edit: Syntax check after user modifications
- **D-35:** Save generated: Code saved to `.algomath/algorithms/{name}/generated.py`
- **D-36:** Proceed gate: User must explicitly approve code before execution

### the agent's Discretion
- Exact template formatting (indentation, spacing)
- LLM prompt engineering for code generation
- Type inference heuristic details
- Complexity calculation approach
- Error message wording
- Code preview UI layout

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Vision, core value, user profile
- `.planning/REQUIREMENTS.md` — GEN-01 to GEN-06 (Generation requirements)
- `.planning/ROADMAP.md` — Phase 3 goal and success criteria

### Prior Phase Context
- `.planning/phases/01-foundation/01-CONTEXT.md` — Foundation decisions (Python language, JSON format)
- `.planning/phases/02-extraction/02-CONTEXT.md` — Extraction decisions (Step types, hybrid approach)

### Existing Codebase
- `src/extraction/schema.py` — Step, Algorithm dataclasses (consumes as input)
- `src/extraction/validation.py` — Validation patterns to reuse
- `src/extraction/errors.py` — Error handling patterns
- `src/workflows/generate.py` — Generation workflow stub

### Research Documents
- `.planning/phases/02-extraction/02-RESEARCH.md` — Reuse generation research section
- `.planning/research/ARCHITECTURE.md` — System data flow

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **StepType enum**: `src/extraction/schema.py` — Use to determine code generation templates
- **Step dataclass**: `src/extraction/schema.py` — Provides step attributes (type, condition, body, etc.)
- **Algorithm dataclass**: `src/extraction/schema.py` — Provides inputs, outputs, steps list
- **ValidationResult**: `src/extraction/validation.py` — Pattern for generation validation results

### Established Patterns
- Hybrid approach (rule + LLM) from extraction → Apply to generation
- Template-based code generation with variable substitution
- Error categorization with user-friendly messages
- Progress indicator integration (show_progress from workflows)
- Side-by-side review interface (reuse review.py patterns)

### Integration Points
- Generation workflow connects to extraction output (Algorithm objects)
- Generated code feeds into execution phase (Phase 4)
- ContextManager saves generated code to `.algomath/algorithms/{name}/generated.py`
- State transitions: CODE_GENERATED after approval

</code_context>

<specifics>
## Specific Ideas

- Generated code should be immediately runnable after review
- Include example usage in docstring when possible
- Preserve algorithm name as function name (converted to snake_case)
- Generated code should be PEP 8 compliant (autopep8 or black formatting optional)
- Include type hints for all numpy operations (e.g., np.ndarray vs ArrayLike)
- Docstrings should reference original algorithm source (paper/citation if available)
- Support common algorithm patterns: initialization loop → process loop → return result

</specifics>

<deferred>
## Deferred Ideas

- Code optimization suggestions — v2 feature (GEN-07)
- Alternative implementation options — v2 feature (GEN-08)
- Automatic test case generation — v2 feature (GEN-09)
- Multi-language generation (JavaScript, C++) — out of scope per PROJECT.md
- GPU acceleration hints — out of scope for v1
- Formal verification annotations — out of scope

</deferred>

---

*Phase: 03-generation*
*Context gathered: 2026-03-30*
