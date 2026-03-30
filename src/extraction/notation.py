"""Mathematical notation normalization for algorithm extraction.

Transforms common mathematical notation into normalized forms
that can be parsed by rule-based and LLM extractors.

Per D-09, D-10, D-11 from 02-CONTEXT.md.
"""
import re
from typing import Tuple, Optional


def normalize_notation(text: str) -> str:
    """
    Normalize mathematical notation in algorithm text.

    Performs transformations in order:
    1. Summation notation (Σ)
    2. Product notation (Π)
    3. Set membership (∈, ∉, ⊆, ⊇, ⊂, ⊃)
    4. Arrow notation (→, ←)
    5. Subscripts (x_i → x[i])
    6. Superscripts (x^2 → x**2)
    7. Mathematical operators (×, ÷, √, ±)

    Args:
        text: Raw algorithm text with mathematical notation

    Returns:
        Normalized text ready for parsing

    Per D-09, D-10 from 02-CONTEXT.md.
    """
    result = text

    # Transform summation and product notation first (multi-line constructs)
    result = transform_summation(result)
    result = transform_product(result)

    # Transform set membership
    result = transform_set_membership(result)

    # Transform arrow notation
    result = transform_arrow_notation(result)

    # Transform subscripts and superscripts
    result = transform_subscripts(result)
    result = transform_superscripts(result)

    # Transform mathematical operators
    result = transform_operators(result)

    return result


def transform_summation(text: str) -> str:
    """
    Transform summation notation Σ into normalized form.

    Patterns handled:
    - Σ_{i=1}^{n} f(i) → sum over i from 1 to n of f(i)
    - Σ_{i∈S} f(i) → sum over i in S of f(i)
    - Σ_{i=1}^{n} Σ_{j=1}^{m} → nested sums

    Per D-09 from 02-CONTEXT.md.
    """
    # Pattern: Σ_{var=range}^{limit} expression
    # Handle nested sums iteratively
    result = text

    # Single summation with range
    pattern1 = r'[Σ\\sum]_\{(\w+)=([^}]+)\}\^\{([^}]+)\}\s*([^(]+?)(?:\(([^)]+)\))?$'
    def replace_sum(match):
        var = match.group(1)
        start = match.group(2)
        end = match.group(3)
        func = match.group(4).strip() if match.group(4) else ""
        arg = match.group(5) if match.group(5) else var
        if func:
            return f"sum over {var} from {start} to {end} of {func}({arg})"
        return f"sum over {var} from {start} to {end}"

    result = re.sub(pattern1, replace_sum, result, flags=re.MULTILINE)

    # Summation over set
    pattern2 = r'[Σ\\sum]_\{(\w+)\s*∈\s*(\w+)\}'
    result = re.sub(pattern2, r'sum over \1 in \2', result)

    return result


def transform_product(text: str) -> str:
    """
    Transform product notation Π into normalized form.

    Patterns handled:
    - Π_{i=1}^{n} f(i) → product over i from 1 to n of f(i)
    - Π_{i∈S} f(i) → product over i in S of f(i)

    Per D-09 from 02-CONTEXT.md.
    """
    result = text

    # Single product with range
    pattern1 = r'[Π\\prod]_\{(\w+)=([^}]+)\}\^\{([^}]+)\}'
    result = re.sub(pattern1, r'product over \1 from \2 to \3', result)

    # Product over set
    pattern2 = r'[Π\\prod]_\{(\w+)\s*∈\s*(\w+)\}'
    result = re.sub(pattern2, r'product over \1 in \2', result)

    return result


def transform_set_membership(text: str) -> str:
    """
    Transform set membership notation into Python equivalents.

    Transformations:
    - x ∈ S → x in S
    - x ∉ S → x not in S
    - A ⊆ B → A.issubset(B) [or A subset of B for description]
    - A ⊂ B → A proper subset of B
    - A ⊇ B → A superset of B
    - A ⊃ B → A proper superset of B

    Per D-09 from 02-CONTEXT.md.
    """
    result = text

    # Not in set
    result = re.sub(r'(\w+)\s*∉\s*(\w+)', r'\1 not in \2', result)

    # In set
    result = re.sub(r'(\w+)\s*∈\s*(\w+)', r'\1 in \2', result)

    # Subset and superset (use natural language for algorithm descriptions)
    result = re.sub(r'(\w+)\s*⊆\s*(\w+)', r'\1 is subset of \2', result)
    result = re.sub(r'(\w+)\s*⊂\s*(\w+)', r'\1 is proper subset of \2', result)
    result = re.sub(r'(\w+)\s*⊇\s*(\w+)', r'\1 is superset of \2', result)
    result = re.sub(r'(\w+)\s*⊃\s*(\w+)', r'\1 is proper superset of \2', result)

    return result


def transform_arrow_notation(text: str) -> str:
    """
    Transform arrow notation into assignments.

    Transformations:
    - x → y → x = y (assignment)
    - x ← y → x = y (assignment)
    - x ↦ y → x maps to y

    Per D-09 from 02-CONTEXT.md.
    """
    result = text

    # Assignment arrows (preserve direction as =)
    result = re.sub(r'(\w+)\s*→\s*(.+?)(?=$|\s+\w+\s*=|\s+[,.])', r'\1 = \2', result)
    result = re.sub(r'(\w+)\s*←\s*(.+?)(?=$|\s+\w+\s*=|\s+[,.])', r'\1 = \2', result)

    return result


def transform_subscripts(text: str) -> str:
    """
    Transform subscript notation into array indexing.

    Transformations:
    - x_i → x[i]
    - x_{i,j} → x[i][j] or x[i, j]
    - A_{i,j} → A[i][j] (matrix access)

    Per D-11 from 02-CONTEXT.md.
    """
    result = text

    # Simple subscript x_i
    result = re.sub(r'(\w+)_\{(\w+)\}', r'\1[\2]', result)
    result = re.sub(r'(\w+)_([a-zA-Z0-9])', r'\1[\2]', result)

    return result


def transform_superscripts(text: str) -> str:
    """
    Transform superscript notation into power notation.

    Transformations:
    - x^2 → x**2
    - x^{n} → x**n
    - x^2_i → x[i]**2 (subscript takes precedence in rendering)

    Per D-11 from 02-CONTEXT.md.
    """
    result = text

    # Braced superscript x^{n}
    result = re.sub(r'(\w+)\^\{(\w+)\}', r'\1**\2', result)

    # Simple superscript x^2 (single char or digit)
    result = re.sub(r'(\w+)\^(\d)', r'\1**\2', result)
    result = re.sub(r'(\w+)\^([a-zA-Z])', r'\1**\2', result)

    return result


def transform_operators(text: str) -> str:
    """
    Transform mathematical operators into Python equivalents.

    Transformations:
    - × → *
    - ÷ → /
    - √x → sqrt(x)
    - ± → +/-
    - ≤ → <=
    - ≥ → >=
    - ≠ → !=

    Per D-10 from 02-CONTEXT.md.
    """
    result = text

    # Comparison operators
    result = result.replace('≤', '<=')
    result = result.replace('≥', '>=')
    result = result.replace('≠', '!=')
    result = result.replace('≈', '~=')

    # Arithmetic operators
    result = result.replace('×', '*')
    result = result.replace('÷', '/')
    result = result.replace('±', '+/-')

    # Square root
    result = re.sub(r'√([\w\[\]]+)', r'sqrt(\1)', result)
    result = re.sub(r'√\{([^}]+)\}', r'sqrt(\1)', result)

    return result
