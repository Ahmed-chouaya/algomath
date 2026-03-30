"""LLM prompts for code generation.

This module provides prompts for generating Python code from
structured algorithms using LLM assistance.
"""

from typing import Any, Dict, List

from src.extraction.schema import Algorithm


# System prompts
CODE_GENERATION_SYSTEM_PROMPT = """You are a Python code generator for mathematical algorithms.

Your task: Generate executable Python code from structured algorithm steps.

Rules:
1. Use type hints for all parameters and return values
2. Include Google-style docstrings with Args, Returns sections
3. Use numpy (np) for matrix/vector operations
4. Use math module for mathematical functions (sqrt, sin, cos, etc.)
5. Follow PEP 8 naming conventions (snake_case)
6. Generate clean, well-formatted code
7. Handle edge cases gracefully

Output format: Return ONLY valid Python code, no markdown fences, no explanations.
"""


CODE_GENERATION_USER_TEMPLATE = """Generate Python code for this algorithm:

Algorithm Name: {name}
Description: {description}

Inputs:
{inputs}

Outputs:
{outputs}

Steps:
{steps}

Requirements:
- Include type hints
- Include comprehensive docstring
- Use numpy for arrays/matrices
- Generate helper functions if needed
- Handle all edge cases

Generate only the Python function code."""


COMPLEX_EXPRESSION_SYSTEM_PROMPT = """You are a Python expression generator.

Convert mathematical expressions into valid Python code.

Examples:
- "sum of A[i] for i from 1 to n" -> "sum(A[i] for i in range(n))"
- "minimum distance from u to v" -> "min(dist[u], dist[v])"
- "argmin of distances" -> "np.argmin(distances)"
- "set of visited nodes" -> "visited = set()"

Use standard Python operators and functions."""


DOCSTRING_GENERATION_PROMPT = """Generate a Google-style docstring for this algorithm.

Include:
- One-line summary
- Detailed description (from algorithm description)
- Args section with types and descriptions
- Returns section with type and description
- Raises section (if applicable)
- Complexity notation (if inferable: O(n), O(n²), etc.)
- Step references (links to step IDs)

Example format:
Triple-quote
{one_line_summary}

{detailed_description}

Args:
{param}: {type} - {description}

Returns:
{type}: {description}

Raises:
ValueError: When {condition}

Time Complexity: {complexity}
Space Complexity: {complexity}
Triple-quote
"""


def format_inputs(inputs: List[Dict[str, Any]]) -> str:
    """Format inputs for prompt."""
    if not inputs:
        return "  (none)"
    lines = []
    for inp in inputs:
        name = inp.get('name', 'unnamed')
        desc = inp.get('description', '')
        lines.append(f"  - {name}: {desc}")
    return '\n'.join(lines)


def format_outputs(outputs: List[Dict[str, Any]]) -> str:
    """Format outputs for prompt."""
    if not outputs:
        return "  (none)"
    lines = []
    for out in outputs:
        name = out.get('name', 'unnamed')
        desc = out.get('description', '')
        lines.append(f"  - {name}: {desc}")
    return '\n'.join(lines)


def format_steps(steps: List[Any]) -> str:
    """Format steps for prompt."""
    if not steps:
        return "  (none)"
    lines = []
    for i, step in enumerate(steps, 1):
        lines.append(f"  {i}. [{step.type.value if hasattr(step, 'type') else 'step'}] {step.description}")
    return '\n'.join(lines)


def format_code_generation_prompt(algorithm: Algorithm) -> List[Dict[str, str]]:
    """
    Format messages for LLM code generation.
    
    Args:
        algorithm: Algorithm to generate code for
        
    Returns:
        List of message dicts for LLM API
    """
    return [
        {"role": "system", "content": CODE_GENERATION_SYSTEM_PROMPT},
        {"role": "user", "content": CODE_GENERATION_USER_TEMPLATE.format(
            name=algorithm.name,
            description=algorithm.description,
            inputs=format_inputs(algorithm.inputs),
            outputs=format_outputs(algorithm.outputs),
            steps=format_steps(algorithm.steps)
        )}
    ]


def format_complex_expression_prompt(expression: str, context: Dict[str, Any] = None) -> List[Dict[str, str]]:
    """
    Format messages for complex expression generation.
    
    Args:
        expression: Mathematical expression to convert
        context: Variable context
        
    Returns:
        List of message dicts for LLM API
    """
    context_str = ""
    if context:
        vars_str = '\n'.join(f"  - {k}: {v}" for k, v in context.items())
        context_str = f"\nAvailable variables:\n{vars_str}"
    
    return [
        {"role": "system", "content": COMPLEX_EXPRESSION_SYSTEM_PROMPT},
        {"role": "user", "content": f"Convert to Python: {expression}{context_str}"}
    ]


def format_docstring_generation_prompt(algorithm: Algorithm) -> List[Dict[str, str]]:
    """
    Format messages for docstring generation.
    
    Args:
        algorithm: Algorithm to generate docstring for
        
    Returns:
        List of message dicts for LLM API
    """
    return [
        {"role": "system", "content": DOCSTRING_GENERATION_PROMPT},
        {"role": "user", "content": f"Generate docstring for algorithm: {algorithm.name}\n\n{algorithm.description}"}
    ]


# Exports
__all__ = [
    "CODE_GENERATION_SYSTEM_PROMPT",
    "CODE_GENERATION_USER_TEMPLATE",
    "COMPLEX_EXPRESSION_SYSTEM_PROMPT",
    "DOCSTRING_GENERATION_PROMPT",
    "format_code_generation_prompt",
    "format_complex_expression_prompt",
    "format_docstring_generation_prompt",
]
