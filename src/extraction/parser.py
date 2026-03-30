"""Rule-based parser for algorithm extraction.

Uses pattern matching and heuristics to extract structured
algorithm steps from mathematical text descriptions.

Per D-02 from 02-CONTEXT.md.
"""
import re
from typing import List, Optional, Dict, Any, Tuple

from .schema import Algorithm, Step, StepType
from .notation import normalize_notation
from .boundaries import (
    find_algorithm_name,
    extract_input_section,
    extract_output_section,
    AlgorithmBoundaries,
    detect_algorithm_boundaries
)


class RuleBasedParser:
    """
    Parser using regex rules to extract algorithm steps.

    Integrates with notation normalization and boundary detection
    to produce structured algorithm representations.

    Per D-02, D-04 from 02-CONTEXT.md.
    """

    def __init__(self):
        # Step detection patterns
        self.step_patterns = [
            # Numbered steps: "1. Do something" or "1) Do something"
            (r'^(?:\s*)(\d+)[.\)]\s*(.+)$', self._parse_numbered_step),
            # Step keyword: "Step 1: Do something"
            (r'^(?:\s*)[Ss]tep\s*(\d+)[:.\)]\s*(.+)$', self._parse_numbered_step),
            # Bullet points as steps
            (r'^(?:\s*)[-*•]\s*(.+)$', self._parse_bullet_step),
        ]

        # Step type detection patterns
        self.type_patterns = [
            (r'^\s*[Rr]eturn', StepType.RETURN),
            (r'^\s*[Oo]utput', StepType.RETURN),
            (r'^\s*[Ff]or\s+each', StepType.LOOP_FOR),
            (r'^\s*[Ff]or\s+\w+\s+(?:from|in|=)', StepType.LOOP_FOR),
            (r'^\s*[Ff]or\s*\(', StepType.LOOP_FOR),
            (r'^\s*[Rr]epeat', StepType.LOOP_FOR),
            (r'^\s*[Ww]hile', StepType.LOOP_WHILE),
            (r'^\s*[Uu]ntil', StepType.LOOP_WHILE),
            (r'^\s*[Ii]f', StepType.CONDITIONAL),
            (r'^\s*[Ww]hen', StepType.CONDITIONAL),
            (r'^\s*[Cc]all\s+\w+\s*\(', StepType.CALL),
            (r'^\s*[Ii]nvoke', StepType.CALL),
        ]

    def parse(self, text: str, name: Optional[str] = None) -> Algorithm:
        """
        Parse text into an Algorithm.

        Args:
            text: Raw algorithm text
            name: Optional algorithm name (auto-detected if not provided)

        Returns:
            Algorithm object with extracted steps

        Per D-02, D-04 from 02-CONTEXT.md.
        """
        # Normalize mathematical notation
        normalized = normalize_notation(text)

        # Detect boundaries
        boundaries = detect_algorithm_boundaries(text)

        # Determine algorithm name
        if not name:
            name = boundaries.name
        if not name:
            name = "unnamed"

        # Extract inputs and outputs
        _, _, input_descs = extract_input_section(text)
        _, _, output_descs = extract_output_section(text)

        # Parse steps
        steps = self._parse_steps(normalized, boundaries)

        return Algorithm(
            name=name,
            inputs=self._parse_inputs(input_descs),
            outputs=self._parse_outputs(output_descs),
            steps=steps,
            source_text=text
        )

    def _parse_steps(self, text: str, boundaries: AlgorithmBoundaries) -> List[Step]:
        """
        Parse steps from normalized text.

        Args:
            text: Normalized text
            boundaries: Detected boundaries

        Returns:
            List of Step objects
        """
        lines = text.split('\n')
        steps = []
        step_id = 1

        # Determine which lines to parse
        start_line = boundaries.steps_start or 1
        end_line = boundaries.steps_end or len(lines)

        for line_num in range(start_line, min(end_line + 1, len(lines) + 1)):
            line = lines[line_num - 1]
            stripped = line.strip()

            if not stripped:
                continue

            # Try to match step patterns
            matched = False
            for pattern, handler in self.step_patterns:
                match = re.match(pattern, line)
                if match:
                    step = handler(match, step_id, line_num)
                    if step:
                        steps.append(step)
                        step_id += 1
                        matched = True
                        break

            # If no pattern matched but line looks like a step
            if not matched and len(stripped) > 10 and not self._is_section_header(stripped):
                step = self._create_step(step_id, StepType.ASSIGNMENT, stripped, line_num)
                steps.append(step)
                step_id += 1

        return steps

    def _parse_numbered_step(self, match, step_id: int, line_num: int) -> Optional[Step]:
        """Parse a numbered step match."""
        # For numbered pattern, group 2 contains the content
        text = match.group(2).strip() if len(match.groups()) > 1 else match.group(1).strip()

        step_type = self._classify_step_type(text)
        return self._create_step(step_id, step_type, text, line_num)

    def _parse_bullet_step(self, match, step_id: int, line_num: int) -> Optional[Step]:
        """Parse a bullet point step."""
        text = match.group(1).strip()
        step_type = self._classify_step_type(text)
        return self._create_step(step_id, step_type, text, line_num)

    def _create_step(self, step_id: int, step_type: StepType, text: str, line_num: int) -> Step:
        """Create a step with extracted metadata."""
        inputs, outputs = self._extract_variables(text)

        # Extract additional fields based on type
        condition = None
        expression = None
        iter_var = None
        iter_range = None

        if step_type == StepType.LOOP_FOR:
            iter_var, iter_range = self._extract_for_loop_details(text)
        elif step_type == StepType.LOOP_WHILE:
            condition = self._extract_while_condition(text)
        elif step_type == StepType.CONDITIONAL:
            condition = self._extract_if_condition(text)
        elif step_type == StepType.RETURN:
            expression = self._extract_return_value(text)
        elif step_type == StepType.ASSIGNMENT:
            expression = self._extract_assignment_expression(text)

        return Step(
            id=step_id,
            type=step_type,
            description=text,
            inputs=inputs,
            outputs=outputs,
            line_refs=[line_num],
            condition=condition,
            expression=expression,
            iter_var=iter_var,
            iter_range=iter_range
        )

    def _classify_step_type(self, text: str) -> StepType:
        """
        Classify step type from text using patterns.

        Returns most specific matching type.
        """
        text_lower = text.lower().strip()

        for pattern, step_type in self.type_patterns:
            if re.search(pattern, text_lower):
                return step_type

        # Check for assignment
        if re.search(r'[=←]|\s+is\s+|\s+gets\s+|\s+set\s+to\s+', text_lower):
            return StepType.ASSIGNMENT

        # Check for function call
        if re.search(r'\w+\s*\([^)]*\)', text_lower):
            return StepType.CALL

        return StepType.COMMENT

    def _extract_variables(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Extract input and output variables from step text.

        Args:
            text: Step description

        Returns:
            Tuple of (input_vars, output_vars)
        """
        inputs = []
        outputs = []

        # Find assignments: x = ..., x ← ..., x gets ..., etc.
        assign_patterns = [
            r'(?:initialize|set)\s+(\w+)',
            r'(\w+)\s*[=←]',
            r'(\w+)\s+is\s+set\s+to',
            r'(\w+)\s+gets',
        ]

        for pattern in assign_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                outputs.append(match.group(1))
                break

        # Find all variable references (avoid keywords)
        keywords = {'for', 'while', 'if', 'else', 'return', 'output',
                    'end', 'then', 'do', 'in', 'to', 'from', 'and', 'or'}

        var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        for match in re.finditer(var_pattern, text):
            var = match.group(1)
            if var not in keywords and var not in outputs:
                inputs.append(var)

        return inputs, outputs

    def _extract_for_loop_details(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract iteration variable and range from for loop."""
        # Pattern: for i from 1 to n
        match = re.search(r'[Ff]or\s+(\w+)\s+(?:from|in)\s+(.+?)(?:\s+to|\s+do|\s*:|$)', text)
        if match:
            return match.group(1), match.group(2)

        # Pattern: for each x in S
        match = re.search(r'[Ff]or\s+each\s+(\w+)\s+in\s+(\w+)', text)
        if match:
            return match.group(1), match.group(2)

        return None, None

    def _extract_while_condition(self, text: str) -> Optional[str]:
        """Extract condition from while loop."""
        match = re.search(r'[Ww]hile\s+(.+?)(?:\s*:|\s+do|\s*$)', text)
        if match:
            return match.group(1).strip()
        return None

    def _extract_if_condition(self, text: str) -> Optional[str]:
        """Extract condition from if statement."""
        match = re.search(r'[Ii]f\s+(.+?)(?:\s*:|\s+then|\s*$)', text)
        if match:
            return match.group(1).strip()
        return None

    def _extract_return_value(self, text: str) -> Optional[str]:
        """Extract return value from return statement."""
        match = re.search(r'[Rr]eturn\s+(.+)$', text)
        if match:
            return match.group(1).strip()
        # Also match Output
        match = re.search(r'[Oo]utput\s+(.+)$', text)
        if match:
            return match.group(1).strip()
        return None

    def _extract_assignment_expression(self, text: str) -> Optional[str]:
        """Extract expression from assignment."""
        match = re.search(r'[=←]\s*(.+)$', text)
        if match:
            return match.group(1).strip()
        return None

    def _is_section_header(self, text: str) -> bool:
        """Check if text is a section header."""
        header_patterns = [
            r'^(?:Input|Output|Algorithm|Procedure|Function|Method)',
            r'^(?:Given|Parameters|Returns|Result)',
        ]
        for pattern in header_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        return False

    def _parse_inputs(self, input_descriptions: List[str]) -> List[Dict[str, Any]]:
        """
        Parse input descriptions into structured format.

        Per D-15 from 02-CONTEXT.md.
        """
        inputs = []

        for desc in input_descriptions:
            # Try to extract variable name and type
            # Pattern: "A[1..n] - array of integers"
            match = re.search(r'(\w+(?:\[[^\]]*\])?)\s*(?:-|,|\s)\s*(.+)', desc)
            if match:
                name = match.group(1)
                type_desc = match.group(2)
                var_type = self._infer_type(type_desc)
            else:
                # Just variable name
                name = desc.strip()
                type_desc = ""
                var_type = "unknown"

            inputs.append({
                "name": name,
                "type": var_type,
                "description": desc
            })

        return inputs

    def _parse_outputs(self, output_descriptions: List[str]) -> List[Dict[str, Any]]:
        """
        Parse output descriptions into structured format.

        Per D-16 from 02-CONTEXT.md.
        """
        outputs = []

        for desc in output_descriptions:
            match = re.search(r'(\w+(?:\[[^\]]*\])?)\s*(?:-|,|\s)\s*(.+)', desc)
            if match:
                name = match.group(1)
                type_desc = match.group(2)
                var_type = self._infer_type(type_desc)
            else:
                name = desc.strip()
                type_desc = ""
                var_type = "unknown"

            outputs.append({
                "name": name,
                "type": var_type,
                "description": desc
            })

        return outputs

    def _infer_type(self, description: str) -> str:
        """Infer variable type from description."""
        desc_lower = description.lower()

        if any(word in desc_lower for word in ['array', 'list', 'sequence']):
            if any(word in desc_lower for word in ['matrix', '2d', 'two-dimensional']):
                return "matrix"
            return "array"
        if any(word in desc_lower for word in ['matrix', 'grid', 'table']):
            return "matrix"
        if any(word in desc_lower for word in ['integer', 'int', 'whole number']):
            return "int"
        if any(word in desc_lower for word in ['float', 'real', 'decimal', 'number']):
            return "float"
        if any(word in desc_lower for word in ['boolean', 'bool', 'true', 'false']):
            return "bool"
        if any(word in desc_lower for word in ['string', 'text']):
            return "str"

        return "unknown"


def parse_algorithm(text: str, name: Optional[str] = None) -> Algorithm:
    """
    Convenience function to parse algorithm text.

    Args:
        text: Algorithm description
        name: Optional algorithm name

    Returns:
        Parsed Algorithm object
    """
    parser = RuleBasedParser()
    return parser.parse(text, name)
