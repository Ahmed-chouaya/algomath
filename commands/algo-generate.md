---
description: "Generate Python code from extracted algorithm steps"
argument-hint: "[--review] [--template-only] [--llm-only]"
tools:
  read: true
  write: true
---

<objective>
Generate executable Python code from structured algorithm steps.
Supports template-based generation (fast, reliable) or LLM-enhanced (for complex expressions).
</objective>

<execution_context>
@/home/milgraph/Projects/algo_framework/src/generation/code_generator.py
@/home/milgraph/Projects/algo_framework/src/generation/llm_generator.py
</execution_context>

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
   - Generate docstring

4. **Generate Step Code**
   - Convert each step to Python
   - Handle loops, conditionals, assignments
   - Preserve variable names
   - Add comments explaining logic

5. **Review Point (if --review)**
   - Display generated code
   - Syntax highlighting
   - Ask for approval
   - Allow editing

6. **Validate Code**
   - Syntax check with Python parser
   - Check for common errors
   - Ensure all variables defined

7. **Save Code**
   - Write to .algomath/algorithms/{name}/generated.py
   - Update metadata.json

8. **Display Summary**
   - Show generated file path
   - Line count
   - Next steps: /algo-run
</process>

<examples>

**Generate with default hybrid mode:**
/algo-generate

**Generate with review:**
/algo-generate --review

**Template-based only (faster):**
/algo-generate --template-only

**LLM-enhanced only (better for complex):**
/algo-generate --llm-only

</examples>

<options>

--review
Show generated code for review before saving

--template-only
Use rule-based generation only (no LLM)

--llm-only
Use LLM for all generation (slower but more accurate)

</options>

<next_steps>
/algo-run - Execute the generated code
/algo-verify - Verify execution results
/algo-status - Check algorithm state
</next_steps>
