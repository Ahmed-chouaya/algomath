---
description: "Generate Python code from extracted algorithm steps"
argument-hint: "[--review] [--template-only] [--llm-only]"
tools:
  read: true
  write: true
  Bash: true
---

<objective>
Generate executable Python code from structured algorithm steps.
Supports template-based generation (fast, reliable) or LLM-enhanced (for complex expressions).
</objective>

<execution>
Execute the code generation by running:

**Option 1 - Using npx (no install required):**
```bash
npx -p algomath-extract algogenerate "$@"
```

**Option 2 - If installed globally:**
```bash
algogenerate "$@"
```

**Option 3 - If installed locally in project:**
```bash
./node_modules/.bin/algogenerate "$@"
```

This will:
1. Load the extracted algorithm from .algomath/algorithms/
2. Generate Python code using template or LLM
3. Save generated code to .algomath/generated/
4. Display generation summary
</execution>

<process>
Execute code generation workflow:


1. **Load Algorithm**
- Read steps.json from current algorithm
- Validate step structure
- Check for completeness

2. **Select Generation Mode**
- Default: Hybrid (template + LLM for complex parts)
- --template-only: Rule-based only (faster)
- --llm-only: Full LLM generation (slower, more accurate)

3. **Generate Function Signature**
- Extract inputs and outputs
- Add type hints
- Create docstring

4. **Generate Step Implementation**
- Convert each step to Python code
- Handle mathematical operations
- Manage variable scope
- Add error handling

5. **Add Helper Functions**
- Generate necessary imports
- Create utility functions
- Add validation

6. **Review Point (if --review)**
- Display generated code
- Ask for approval
- Allow regeneration with feedback

7. **Save Generated Code**
- Save to .algomath/generated/{name}.py
- Create __init__.py for imports
- Add requirements.txt if needed

8. **Display Summary**
- Show file path
- Display code preview
- Suggest: /algo-run
</process>

<examples>

**Generate with review:**
/algo-generate

**Auto-generate:**
/algo-generate --auto

**Template-only (faster):**
/algo-generate --template-only

**LLM-enhanced (better for complex math):**
/algo-generate --llm-only

</examples>

<options>

--auto
Skip review, generate automatically

--template-only
Use only template-based generation (faster, no LLM)

--llm-only
Use only LLM generation (slower, handles complex expressions)

--review
Force review mode even in auto mode

</options>

<next_steps>
/algo-run - Execute the generated code
/algo-verify - Verify the generated code
/algo-status - Check current state
</next_steps>
