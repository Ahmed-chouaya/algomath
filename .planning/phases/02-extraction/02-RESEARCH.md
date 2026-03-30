# Phase 2: Extraction - Research

**Research Date:** 2026-03-30
**Phase:** Extraction (Convert mathematical text descriptions into structured algorithm steps)

---

## Extraction Approaches Analyzed

### Hybrid Approach (Selected per D-01)

**Why Hybrid (Rule-based + LLM):**
- Rule-based handles notation normalization (fast, deterministic)
- LLM handles semantic understanding (flexible, context-aware)
- Provides fallback if LLM fails (rule-based still produces output)
- Enables iterative refinement (LLM can improve rule-based output)

### Alternatives Considered

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| Pure Rule-based | Fast, predictable, no API cost | Brittle with variations, misses context | ❌ Too rigid |
| Pure LLM | Handles variety, understands intent | Slower, API-dependent, can hallucinate | ❌ Too unreliable |
| Hybrid (Selected) | Best of both worlds | More complex | ✅ Selected |

---

## Rule-Based Pre-processing Layer

### Mathematical Notation Patterns

**Summation (Σ) → Loop with Accumulator:**
```
Pattern: Σ_{i=1}^{n} f(i)
Transform: sum = 0; for i in range(1, n+1): sum += f(i)
```

**Product (Π) → Loop with Multiplication:**
```
Pattern: Π_{i=1}^{n} f(i)
Transform: prod = 1; for i in range(1, n+1): prod *= f(i)
```

**Set Membership (∈, ⊆):**
```
Pattern: x ∈ S
Transform: x in S (Python)

Pattern: A ⊆ B
Transform: A.issubset(B)
```

**Arrow Notation (→):**
```
Pattern: x → y
Transform: x = y (assignment)
Or: x maps to y (function)
```

**Subscripts and Superscripts:**
```
Pattern: x_i
Transform: x[i]

Pattern: x^2
Transform: x**2

Pattern: x_i^2
Transform: x[i]**2
```

### Algorithm Boundary Detection Patterns

**Headers to detect:**
- "Algorithm X"
- "Procedure Y"
- "Function Z"
- "Method W"
- "Input:" / "Input" (section header)
- "Output:" / "Output" (section header)
- "Returns:" / "Returns" (section header)

**Structural boundaries:**
- Empty lines (paragraph breaks)
- Numbered steps (1., 2., etc.)
- Bullet points (-, *, •)
- Indentation changes

---

## LLM Extraction Strategy

### Structured Output Format (JSON Schema)

```json
{
  "algorithm": {
    "name": "string",
    "description": "string",
    "inputs": [
      {
        "name": "string",
        "type": "string (inferred: int, float, array, matrix, bool)",
        "description": "string"
      }
    ],
    "outputs": [
      {
        "name": "string",
        "type": "string",
        "description": "string"
      }
    ],
    "steps": [
      {
        "id": "integer",
        "type": "string (assignment|loop|conditional|return|call|comment)",
        "description": "string (human-readable)",
        "inputs": ["string array - variables read"],
        "outputs": ["string array - variables written"],
        "line_refs": ["integer array - line numbers in source"],
        "condition": "string (for conditionals/loops)",
        "body": ["step ids (for loops/conditionals)"],
        "else_body": ["step ids (for conditionals)"],
        "iter_var": "string (for loops)",
        "iter_range": "string (for loops)",
        "expression": "string (for assignments)"
      }
    ],
    "source_text": "string (original text with line numbers)"
  }
}
```

### LLM Prompt Engineering

**System Prompt Focus:**
- Parse algorithmic structure from mathematical text
- Identify inputs, outputs, and step sequence
- Handle common mathematical constructs
- Output must be valid JSON
- Preserve line references for user review

**User Prompt Structure:**
```
Extract the algorithm from this mathematical text:

{numbered_source_text}

Provide a structured JSON representation including:
1. Algorithm name (inferred or "unnamed")
2. List of inputs with inferred types
3. List of outputs with types
4. Step-by-step breakdown with:
   - Step type (assignment, loop, conditional, return, call, comment)
   - Description in plain language
   - Input/output variables
   - Source line references
   - Control flow details

Return ONLY the JSON. No explanatory text outside the JSON.
```

---

## Input/Output Detection Strategy

### Explicit Section Detection

**Input sections (look for):**
- "Input:" / "Input" + colon or newline
- "Given:" / "Given"
- "Parameters:" / "Parameters"
- "Takes:" / "Takes"
- "Requires:" / "Requires"

**Output sections (look for):**
- "Output:" / "Output"
- "Returns:" / "Returns"
- "Result:" / "Result"
- "Produces:" / "Produces"

### Implicit Detection (LLM-based)

**Input indicators:**
- Variables appearing on right-hand side before being defined
- Function arguments
- "Given" statements
- Pre-conditions

**Output indicators:**
- "Return" statements
- "Output" statements
- "Result" mentions
- Post-conditions
- Variables at the end of the algorithm

---

## Step Types and Parsing Rules

### Assignment Step
**Pattern:** `variable = expression` or `variable ← expression`
**Fields:**
- `expression`: The assignment expression
- `inputs`: Variables read in expression
- `outputs`: Variable being assigned

### Loop Step (For)
**Pattern:** "For each X in Y:", "For i from 1 to n:", "Repeat n times:"
**Fields:**
- `iter_var`: Loop variable
- `iter_range`: Range specification
- `body`: Step IDs within the loop

### Loop Step (While)
**Pattern:** "While condition:", "Until condition:"
**Fields:**
- `condition`: Loop condition
- `body`: Step IDs within the loop

### Conditional Step
**Pattern:** "If condition:", "When condition:", "In case condition:"
**Fields:**
- `condition`: Branch condition
- `body`: Step IDs for true branch
- `else_body`: Step IDs for false branch (optional)

### Return Step
**Pattern:** "Return X", "Output X", "Result: X"
**Fields:**
- `expression`: The return value

### Call Step
**Pattern:** "Call Function()", "Invoke Procedure"
**Fields:**
- `call_target`: Function/procedure name
- `arguments`: List of arguments passed

### Comment Step
**Pattern:** Explanatory text, annotations, notes
**Fields:**
- `annotation`: The comment text

---

## User Review Interface Requirements

### Side-by-Side View

```
┌─────────────────────────────────────────────────────────────┐
│ Algorithm: {name}                                           │
├──────────────────────────────┬──────────────────────────────┤
│ Original Text                │ Structured Steps             │
│                              │                              │
│ 1. Initialize sum = 0        │ [1] Assignment                │
│                              │     sum = 0                   │
│ 2. For i from 1 to n:        │                              │
│                              │ [2] Loop (For)                │
│    a. Add x[i] to sum        │     For i in range(1, n+1): │
│                              │                              │
│ 3. Return sum                │ [2a] Assignment              │
│                              │     sum += x[i]               │
│                              │                              │
│                              │ [3] Return                    │
│                              │     return sum                │
│                              │                              │
├──────────────────────────────┴──────────────────────────────┤
│ Actions: [Edit Step] [Reorder] [Delete] [Add Step] [✓ Approve] │
└─────────────────────────────────────────────────────────────┘
```

### Edit Capabilities

**Step Editing:**
- Edit description
- Change step type
- Modify inputs/outputs
- Adjust line references

**Step Management:**
- Reorder (drag or up/down arrows)
- Delete with confirmation
- Add new step (insert at position)

**Validation:**
- Step type must be valid
- Inputs/outputs must be string arrays
- IDs must be unique

---

## Error Handling Strategy

### Error Categories

1. **ParseError:** Syntax errors in notation
   - Example: Unmatched parentheses in Σ expression
   - Response: "Could not parse summation notation at line X"

2. **AmbiguityError:** Multiple valid interpretations
   - Example: "x → y" could be assignment or function mapping
   - Response: "Ambiguous arrow notation at line X - is this assignment or mapping?"

3. **IncompleteError:** Missing information
   - Example: Algorithm ends mid-description
   - Response: "Algorithm appears incomplete - no clear termination at line X"

### Retry Mechanism

**User Clarification Flow:**
1. System identifies unclear section
2. Presents partial extraction
3. Asks for clarification
4. Re-runs extraction with additional context

---

## Performance Considerations

### Timeouts
- Total extraction: 30 seconds maximum
- Rule-based layer: < 1 second
- LLM call: 20-25 seconds (with retry)

### Progress Indicators
```
Extract: Parsing notation... ████░░░░░░ 40%
Extract: Analyzing structure... ███████░░░ 70%
Extract: Validating output... █████████░ 90%
Extract: Complete ✓
```

### Streaming
- Display extracted steps as they are identified
- Update side-by-side view incrementally
- Finalize with validation

---

## Testing Strategy

### Test Cases Needed

1. **Simple summation** (Σ notation)
2. **Matrix multiplication** (double loops, subscripts)
3. **Conditional logic** (if/then/else)
4. **Recursive definition** (self-reference)
5. **Edge cases** (empty input, malformed text)

### Validation Tests
- JSON schema validation
- Step connectivity (all referenced steps exist)
- Variable flow (all inputs are defined before use)

---

## Implementation Dependencies

**From Phase 1 (Foundation):**
- ContextManager.save_steps() for persistence
- WorkflowState.STEPS_STRUCTURED state transition
- Progress indicator format from src/workflows/extract.py

**New Dependencies:**
- jsonschema (for JSON validation)
- No external LLM API library (use the agent's native capabilities)

---

## Canonical References

- `src/workflows/extract.py` — Current stub implementation
- `.algomath/context.py` — ContextManager with save_steps()
- `.algomath/state.py` — WorkflowState.STEPS_STRUCTURED
- `.planning/phases/02-extraction/02-CONTEXT.md` — User decisions (D-01 to D-29)

---

*Research for Phase 2: Extraction*
*Generated by gsd-phase-researcher*
