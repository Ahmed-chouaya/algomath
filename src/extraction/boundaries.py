"""Algorithm boundary detection for extraction.

Identifies algorithm sections including headers, inputs, outputs,
and step boundaries within mathematical text.

Per D-12, D-13, D-14, D-15, D-16, D-17 from 02-CONTEXT.md.
"""
import re
from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass


@dataclass
class AlgorithmBoundaries:
    """Represents detected algorithm boundaries."""
    name: str
    name_line: Optional[int] = None
    input_start: Optional[int] = None
    input_end: Optional[int] = None
    output_start: Optional[int] = None
    output_end: Optional[int] = None
    steps_start: Optional[int] = None
    steps_end: Optional[int] = None


# Patterns for detecting algorithm headers
HEADER_PATTERNS = [
    r'^\s*(?:Algorithm|ALGORITHM)[\s:]+([A-Za-z][A-Za-z0-9_\s]*)',
    r'^\s*(?:Procedure|PROCEDURE)[\s:]+([A-Za-z][A-Za-z0-9_\s]*)',
    r'^\s*(?:Function|FUNCTION)[\s:]+([A-Za-z][A-Za-z0-9_\s]*)',
    r'^\s*(?:Method|METHOD)[\s:]+([A-Za-z][A-Za-z0-9_\s]*)',
]

# Patterns for input sections
INPUT_PATTERNS = [
    r'^\s*(?:Input|INPUT|Inputs|INPUTS)[\s:]*',
    r'^\s*(?:Given|GIVEN)[\s:]*',
    r'^\s*(?:Parameters|PARAMETERS)[\s:]*',
    r'^\s*(?:Takes|TAKES)[\s:]*',
    r'^\s*(?:Requires|REQUIRES)[\s:]*',
    r'^\s*(?:Precondition|PRECONDITION)[\s:]*',
]

# Patterns for output sections
OUTPUT_PATTERNS = [
    r'^\s*(?:Output|OUTPUT|Outputs|OUTPUTS)[\s:]*',
    r'^\s*(?:Returns|RETURNS)[\s:]*',
    r'^\s*(?:Result|RESULT|Results|RESULTS)[\s:]*',
    r'^\s*(?:Produces|PRODUCES)[\s:]*',
    r'^\s*(?:Postcondition|POSTCONDITION)[\s:]*',
]


def find_algorithm_name(text: str) -> Tuple[str, Optional[int]]:
    """
    Find algorithm name from header.

    Searches for patterns like:
    - "Algorithm: Name"
    - "Algorithm Name"
    - "Procedure: Name"
    - "Function Name"

    Args:
        text: Algorithm text

    Returns:
        Tuple of (name, line_number) or ("unnamed", None)

    Per D-13 from 02-CONTEXT.md.
    """
    lines = text.split('\n')

    for line_num, line in enumerate(lines, 1):
        for pattern in HEADER_PATTERNS:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up the name
                name = re.sub(r'\s+', ' ', name)
                if name:
                    return name, line_num

    return "unnamed", None


def extract_input_section(text: str) -> Tuple[Optional[int], Optional[int], List[str]]:
    """
    Extract input section from algorithm text.

    Identifies input section boundaries and returns the content.

    Args:
        text: Algorithm text

    Returns:
        Tuple of (start_line, end_line, input_descriptions)
        Lines are 1-indexed, None if not found

    Per D-15 from 02-CONTEXT.md.
    """
    lines = text.split('\n')
    start_line = None
    end_line = None

    # Find input section header
    for line_num, line in enumerate(lines, 1):
        for pattern in INPUT_PATTERNS:
            if re.match(pattern, line, re.IGNORECASE):
                start_line = line_num
                break
        if start_line:
            break

    if not start_line:
        return None, None, []

    # Extract input descriptions until next section or end
    input_descriptions = []
    end_line = start_line

    for line_num in range(start_line, len(lines) + 1):
        line = lines[line_num - 1]

        # Check for end of input section (output section or steps)
        if line_num > start_line:
            if _is_section_boundary(line):
                break

        # Skip the header line itself
        if line_num == start_line:
            # Remove header part
            clean_line = re.sub(r'^\s*(?:Input|INPUT)[\s:]*', '', line).strip()
            if clean_line:
                input_descriptions.append(clean_line)
        else:
            stripped = line.strip()
            if stripped and not _is_section_boundary(line):
                input_descriptions.append(stripped)

        end_line = line_num

    return start_line, end_line, input_descriptions


def extract_output_section(text: str) -> Tuple[Optional[int], Optional[int], List[str]]:
    """
    Extract output section from algorithm text.

    Identifies output section boundaries and returns the content.

    Args:
        text: Algorithm text

    Returns:
        Tuple of (start_line, end_line, output_descriptions)
        Lines are 1-indexed, None if not found

    Per D-16 from 02-CONTEXT.md.
    """
    lines = text.split('\n')
    start_line = None
    end_line = None

    # Find output section header
    for line_num, line in enumerate(lines, 1):
        for pattern in OUTPUT_PATTERNS:
            if re.match(pattern, line, re.IGNORECASE):
                start_line = line_num
                break
        if start_line:
            break

    if not start_line:
        return None, None, []

    # Extract output descriptions until next section or end
    output_descriptions = []
    end_line = start_line

    for line_num in range(start_line, len(lines) + 1):
        line = lines[line_num - 1]

        # Check for end of output section
        if line_num > start_line:
            if _is_section_boundary(line):
                break

        # Skip the header line itself
        if line_num == start_line:
            clean_line = re.sub(r'^\s*(?:Output|OUTPUT)[\s:]*', '', line).strip()
            if clean_line:
                output_descriptions.append(clean_line)
        else:
            stripped = line.strip()
            if stripped and not _is_section_boundary(line):
                output_descriptions.append(stripped)

        end_line = line_num

    return start_line, end_line, output_descriptions


def detect_algorithm_boundaries(text: str) -> AlgorithmBoundaries:
    """
    Detect all algorithm boundaries in text.

    Per D-12, D-13, D-14 from 02-CONTEXT.md.

    Args:
        text: Algorithm text

    Returns:
        AlgorithmBoundaries with detected sections
    """
    name, name_line = find_algorithm_name(text)

    input_start, input_end, _ = extract_input_section(text)
    output_start, output_end, _ = extract_output_section(text)

    # Detect steps section (after outputs or after name if no I/O)
    lines = text.split('\n')
    steps_start = None
    steps_end = len(lines)

    # Start after the latest of: name, input, output
    potential_start = name_line or 1
    if input_end:
        potential_start = max(potential_start, input_end + 1)
    if output_end:
        potential_start = max(potential_start, output_end + 1)

    # Look for numbered steps
    for line_num in range(potential_start, len(lines) + 1):
        line = lines[line_num - 1]
        if re.match(r'^\s*\d+[.\)]\s+', line) or re.match(r'^\s*[Ss]tep\s+\d+', line):
            steps_start = line_num
            break

    # If no numbered steps found, use the line after sections
    if not steps_start:
        steps_start = potential_start

    return AlgorithmBoundaries(
        name=name,
        name_line=name_line,
        input_start=input_start,
        input_end=input_end,
        output_start=output_start,
        output_end=output_end,
        steps_start=steps_start,
        steps_end=steps_end
    )


def _is_section_boundary(line: str) -> bool:
    """
    Check if line marks a section boundary.

    Returns True for:
    - Empty lines (double newline)
    - Output headers after input
    - Step indicators
    - Algorithm boundaries
    """
    stripped = line.strip()

    if not stripped:
        return True

    # Check for section headers
    all_headers = HEADER_PATTERNS + INPUT_PATTERNS + OUTPUT_PATTERNS
    for pattern in all_headers:
        if re.match(pattern, line, re.IGNORECASE):
            return True

    # Check for numbered steps
    if re.match(r'^\s*\d+[.\)]', line):
        return True

    return False
