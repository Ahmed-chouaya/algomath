"""LLM prompts for algorithm extraction.

This module provides system and user prompts for LLM-based algorithm extraction,
designed to guide the LLM to produce structured JSON output.
"""

EXTRACTION_SYSTEM_PROMPT = """You are an expert at parsing mathematical algorithms from natural language descriptions.

Your task is to analyze algorithm text and extract a structured JSON representation.

RULES:
1. Identify the algorithm name from headers like "Algorithm X", "Procedure Y"
2. Extract inputs and outputs from Input/Output sections
3. Parse each step with accurate type classification
4. Preserve line references to the original text
5. Handle mathematical notation (Σ, Π, subscripts, superscripts)
6. Output valid JSON only - no explanatory text

STEP TYPES (classify each step):
- assignment: Variable assignment (x = y, x ← y)
- loop_for: For loops (for each, for i from, repeat n times)
- loop_while: While loops (while condition, until condition)
- conditional: If statements (if, when, in case)
- return: Return statements (return x, output x, result)
- call: Function calls (call f(), invoke)
- comment: Annotations and explanations

JSON OUTPUT FORMAT:
{
  "name": "algorithm name or 'unnamed'",
  "description": "brief description",
  "inputs": [{"name": "var", "type": "inferred", "description": ""}],
  "outputs": [{"name": "var", "type": "inferred", "description": ""}],
  "steps": [
    {
      "id": 1,
      "type": "assignment",
      "description": "human readable description",
      "inputs": ["read vars"],
      "outputs": ["written vars"],
      "line_refs": [line_numbers],
      "condition": null,
      "body": [],
      "else_body": [],
      "iter_var": null,
      "iter_range": null,
      "expression": null,
      "call_target": null,
      "arguments": [],
      "annotation": null
    }
  ],
  "source_text": "original text with line numbers"
}

Infer types: int, float, array, matrix, bool based on context.
Always include line_refs array showing which original lines this step came from."""

EXTRACTION_USER_PROMPT_TEMPLATE = """Extract the algorithm from this mathematical text:

```
{numbered_text}
```

Provide the structured JSON representation following the schema provided.

Return ONLY the JSON. No explanatory text outside the JSON."""


def format_extraction_prompt(text: str) -> str:
    """
    Format extraction prompt with numbered text.

    Args:
        text: Raw algorithm text

    Returns:
        Formatted prompt with line numbers for traceability

    Per D-08 from 02-CONTEXT.md.
    """
    lines = text.split('\n')
    numbered_lines = []

    for i, line in enumerate(lines, 1):
        numbered_lines.append(f"{i:3d}: {line}")

    numbered_text = '\n'.join(numbered_lines)

    return EXTRACTION_USER_PROMPT_TEMPLATE.format(numbered_text=numbered_text)
