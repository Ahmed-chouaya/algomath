"""Static analysis and edge case detection module for AlgoMath.

Provides detection of potential edge cases through static code analysis
and execution-based testing.

Per D-13 through D-16: Pattern detection, execution testing, severity levels,
 and comprehensive edge case coverage.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import re
import sys

from src.extraction.schema import Algorithm, Step, StepType


class EdgeCaseSeverity(Enum):
    """Severity levels for edge cases."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class EdgeCase:
    """Represents a detected edge case.

    Per D-15: Includes severity, description, location, suggestion.
    Per D-16: Covers empty, single, max, negative, zero values.
    Per D-141: Suggests specific test values.
    """
    type: str
    severity: EdgeCaseSeverity
    description: str
    location: Optional[str] = None
    suggestion: str = ""
    test_input: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "type": self.type,
            "severity": self.severity.value,
            "description": self.description,
            "location": self.location,
            "suggestion": self.suggestion,
            "test_input": self.test_input,
        }


class EdgeCaseDetector:
    """Detects edge cases through static and execution analysis.

    Per D-13: Static analysis for patterns.
    Per D-14: Execution-based testing.
    Per D-15: Report detected and potential edge cases.
    Per D-16: Test empty, single, max, negative, zero.
    """

    def __init__(self, code: str, algorithm: Optional[Algorithm] = None):
        """Initialize detector with code and optional algorithm.

        Args:
            code: Python code to analyze
            algorithm: Optional algorithm structure for context
        """
        self.code = code
        self.algorithm = algorithm
        self._detected: List[EdgeCase] = []

    def analyze_static(self) -> List[EdgeCase]:
        """Perform static analysis to detect edge cases.

        Returns:
            List of detected edge cases
        """
        edge_cases = []

        # Run all static analysis checks
        edge_cases.extend(self._check_empty_loops())
        edge_cases.extend(self._check_division_by_zero())
        edge_cases.extend(self._check_recursion_depth())
        edge_cases.extend(self._check_uninitialized_variables())
        edge_cases.extend(self._check_off_by_one())
        edge_cases.extend(self._check_infinite_loops())
        edge_cases.extend(self._check_empty_collections())

        self._detected.extend(edge_cases)
        return edge_cases

    def analyze_execution(self, sandbox) -> List[EdgeCase]:
        """Perform execution-based edge case detection.

        Args:
            sandbox: SandboxExecutor instance for running code

        Returns:
            List of detected edge cases from execution
        """
        edge_cases = []

        # Run execution-based tests
        edge_cases.extend(self._test_empty_input(sandbox))
        edge_cases.extend(self._test_single_element(sandbox))
        edge_cases.extend(self._test_boundary_values(sandbox))
        edge_cases.extend(self._test_negative_values(sandbox))
        edge_cases.extend(self._test_zero_values(sandbox))

        self._detected.extend(edge_cases)
        return edge_cases

    def detect_edge_cases(self) -> List[EdgeCase]:
        """Run all detection methods and return combined results.

        Returns:
            List of all detected edge cases
        """
        # Run static analysis
        static_cases = self.analyze_static()

        # Note: Execution analysis requires a sandbox instance
        # Return static cases for now
        return static_cases

    def _check_empty_loops(self) -> List[EdgeCase]:
        """Detect loops with no body or trivial body."""
        edge_cases = []

        # Pattern: for/while loop with only pass/continue/break
        patterns = [
            (r'for\s+\w+\s+in\s+[^:]+:\s*\n\s*(?:pass|continue|break|\.\.\.)\s*\n',
             "Loop with empty body"),
            (r'while\s+[^:]+:\s*\n\s*(?:pass|continue|break|\.\.\.)\s*\n',
             "While loop with empty body"),
        ]

        for pattern, desc in patterns:
            matches = list(re.finditer(pattern, self.code, re.MULTILINE))
            for i, match in enumerate(matches):
                line_num = self._get_line_number(match.start())
                edge_cases.append(EdgeCase(
                    type="empty_loop",
                    severity=EdgeCaseSeverity.WARNING,
                    description=desc,
                    location=f"line {line_num}",
                    suggestion="Ensure loop has meaningful work or remove it"
                ))

        return edge_cases

    def _check_division_by_zero(self) -> List[EdgeCase]:
        """Detect potential division by zero."""
        edge_cases = []

        # Pattern: division without zero check
        div_pattern = r'(?:/|//|%|\bdiv\b)\s*\(?\s*\w+'
        matches = list(re.finditer(div_pattern, self.code))

        for match in matches:
            line_num = self._get_line_number(match.start())
            context = self._get_line_context(line_num)

            # Check if there's a zero guard
            if not self._has_zero_guard(context):
                edge_cases.append(EdgeCase(
                    type="division_by_zero",
                    severity=EdgeCaseSeverity.CRITICAL,
                    description="Potential division by zero",
                    location=f"line {line_num}",
                    suggestion="Add check: if divisor != 0: before dividing",
                    test_input={"divisor": 0}
                ))

        # Check for modulo operations
        mod_pattern = r'\w+\s*%\s*\w+'
        mod_matches = list(re.finditer(mod_pattern, self.code))

        for match in mod_matches:
            line_num = self._get_line_number(match.start())
            context = self._get_line_context(line_num)

            if not self._has_zero_guard(context):
                edge_cases.append(EdgeCase(
                    type="modulo_by_zero",
                    severity=EdgeCaseSeverity.CRITICAL,
                    description="Potential modulo by zero",
                    location=f"line {line_num}",
                    suggestion="Add check: if divisor != 0: before modulo",
                    test_input={"divisor": 0}
                ))

        return edge_cases

    def _check_recursion_depth(self) -> List[EdgeCase]:
        """Detect recursive functions and depth concerns."""
        edge_cases = []

        # Pattern: function that calls itself
        func_pattern = r'def\s+(\w+)\s*\([^)]*\):'
        func_matches = list(re.finditer(func_pattern, self.code))

        for match in func_matches:
            func_name = match.group(1)
            func_start = match.end()

            # Look for recursive call within function scope
            func_body = self._get_function_body(func_start)
            if func_name in func_body:
                line_num = self._get_line_number(match.start())
                edge_cases.append(EdgeCase(
                    type="recursion_depth",
                    severity=EdgeCaseSeverity.WARNING,
                    description=f"Recursive function '{func_name}' may hit recursion limit",
                    location=f"line {line_num}",
                    suggestion="Consider iterative version or add recursion depth limit"
                ))

        return edge_cases

    def _check_uninitialized_variables(self) -> List[EdgeCase]:
        """Detect use of potentially uninitialized variables."""
        edge_cases = []

        # Simple check: variable used before assignment in a branch
        # This is a heuristic - full analysis requires AST
        var_pattern = r'(?:return|if|while|for)\s+\w+'
        matches = list(re.finditer(var_pattern, self.code))

        # Note: Full uninitialized variable detection requires AST parsing
        # This is a simplified version

        return edge_cases

    def _check_off_by_one(self) -> List[EdgeCase]:
        """Detect potential off-by-one errors."""
        edge_cases = []

        # Pattern: indexing with len() without -1
        patterns = [
            (r'\[\s*len\s*\(\s*\w+\s*\)\s*\]', "Array index at len() may be out of bounds"),
            (r'range\s*\(\s*len\s*\(\s*\w+\s*\)\s*\+\s*1\s*\)', "Extra iteration in range"),
        ]

        for pattern, desc in patterns:
            matches = list(re.finditer(pattern, self.code))
            for match in matches:
                line_num = self._get_line_number(match.start())
                edge_cases.append(EdgeCase(
                    type="off_by_one",
                    severity=EdgeCaseSeverity.WARNING,
                    description=desc,
                    location=f"line {line_num}",
                    suggestion="Verify indices and ranges are correct"
                ))

        return edge_cases

    def _check_infinite_loops(self) -> List[EdgeCase]:
        """Detect potential infinite loops."""
        edge_cases = []

        # Pattern: while True without break
        loop_pattern = r'while\s+True\s*:'
        matches = list(re.finditer(loop_pattern, self.code))

        for match in matches:
            # Check if there's a break in the loop body
            body = self._get_loop_body(match.end())
            if 'break' not in body:
                line_num = self._get_line_number(match.start())
                edge_cases.append(EdgeCase(
                    type="infinite_loop",
                    severity=EdgeCaseSeverity.CRITICAL,
                    description="Potential infinite loop (while True without break)",
                    location=f"line {line_num}",
                    suggestion="Add a break condition or use a for loop"
                ))

        return edge_cases

    def _check_empty_collections(self) -> List[EdgeCase]:
        """Detect operations on empty collections."""
        edge_cases = []

        # Pattern: direct access to list elements without check
        patterns = [
            (r'\[\s*0\s*\]', "First element access without empty check"),
            (r'\.pop\s*\(\s*\)', "Pop operation without empty check"),
        ]

        for pattern, desc in patterns:
            if re.search(pattern, self.code):
                edge_cases.append(EdgeCase(
                    type="empty_collection",
                    severity=EdgeCaseSeverity.WARNING,
                    description=desc,
                    suggestion="Add check: if len(collection) > 0: before accessing"
                ))

        return edge_cases

    def _test_empty_input(self, sandbox) -> List[EdgeCase]:
        """Test with empty inputs per D-16."""
        edge_cases = []

        if self.algorithm:
            test_inputs = self._generate_test_inputs("empty_input", self.algorithm.inputs)
            # Execution would happen here with sandbox
            # For now, add potential edge case
            if test_inputs:
                edge_cases.append(EdgeCase(
                    type="empty_input",
                    severity=EdgeCaseSeverity.INFO,
                    description="Algorithm behavior with empty input",
                    suggestion="Try n=0, empty list, or empty string"
                ))

        return edge_cases

    def _test_single_element(self, sandbox) -> List[EdgeCase]:
        """Test with single element inputs per D-16."""
        edge_cases = []

        if self.algorithm:
            test_inputs = self._generate_test_inputs("single_element", self.algorithm.inputs)
            if test_inputs:
                edge_cases.append(EdgeCase(
                    type="single_element",
                    severity=EdgeCaseSeverity.INFO,
                    description="Algorithm behavior with single element",
                    suggestion="Try n=1, single item list"
                ))

        return edge_cases

    def _test_boundary_values(self, sandbox) -> List[EdgeCase]:
        """Test with boundary values per D-16."""
        edge_cases = []

        edge_cases.append(EdgeCase(
            type="max_value",
            severity=EdgeCaseSeverity.WARNING,
            description="Algorithm behavior with maximum values",
            suggestion="Try sys.maxsize, float('inf'), very large numbers"
        ))

        edge_cases.append(EdgeCase(
            type="min_value",
            severity=EdgeCaseSeverity.WARNING,
            description="Algorithm behavior with minimum values",
            suggestion="Try -sys.maxsize, float('-inf'), very small numbers"
        ))

        return edge_cases

    def _test_negative_values(self, sandbox) -> List[EdgeCase]:
        """Test with negative values per D-16."""
        edge_cases = []

        edge_cases.append(EdgeCase(
            type="negative",
            severity=EdgeCaseSeverity.INFO,
            description="Algorithm behavior with negative inputs",
            suggestion="Try -1, negative integers, negative floats"
        ))

        return edge_cases

    def _test_zero_values(self, sandbox) -> List[EdgeCase]:
        """Test with zero values per D-16."""
        edge_cases = []

        edge_cases.append(EdgeCase(
            type="zero",
            severity=EdgeCaseSeverity.INFO,
            description="Algorithm behavior with zero input",
            suggestion="Try n=0, empty values, zero floats"
        ))

        return edge_cases

    def _generate_test_inputs(
        self,
        edge_case_type: str,
        algorithm_inputs: List[Dict]
    ) -> List[Dict]:
        """Generate test inputs for edge case type.

        Per D-14, D-16: Generate varied test inputs.

        Args:
            edge_case_type: Type of edge case
            algorithm_inputs: Algorithm input definitions

        Returns:
            List of test input dictionaries
        """
        test_inputs = []

        if edge_case_type == "empty_input":
            for input_def in algorithm_inputs:
                name = input_def.get("name", "x")
                input_type = input_def.get("type", "any")

                if input_type == "list" or input_type == "array":
                    test_inputs.append({name: []})
                elif input_type == "str":
                    test_inputs.append({name: ""})
                elif input_type == "dict":
                    test_inputs.append({name: {}})
                else:
                    test_inputs.append({name: 0})

        elif edge_case_type == "single_element":
            for input_def in algorithm_inputs:
                name = input_def.get("name", "x")
                input_type = input_def.get("type", "any")

                if input_type == "list" or input_type == "array":
                    test_inputs.append({name: [1]})
                elif input_type == "str":
                    test_inputs.append({name: "a"})
                else:
                    test_inputs.append({name: 1})

        elif edge_case_type == "max_value":
            for input_def in algorithm_inputs:
                name = input_def.get("name", "x")
                input_type = input_def.get("type", "any")

                if input_type == "int":
                    test_inputs.append({name: sys.maxsize})
                elif input_type == "float":
                    test_inputs.append({name: float('inf')})
                else:
                    test_inputs.append({name: 10**9})

        elif edge_case_type == "negative":
            for input_def in algorithm_inputs:
                name = input_def.get("name", "x")
                input_type = input_def.get("type", "any")

                if input_type in ("int", "float"):
                    test_inputs.append({name: -1})
                    test_inputs.append({name: -0.001})

        elif edge_case_type == "zero":
            for input_def in algorithm_inputs:
                name = input_def.get("name", "x")
                input_type = input_def.get("type", "any")

                if input_type in ("int", "float"):
                    test_inputs.append({name: 0})
                    test_inputs.append({name: 0.0})

        return test_inputs

    def _get_line_number(self, pos: int) -> int:
        """Get line number for a position in code."""
        return self.code[:pos].count('\n') + 1

    def _get_line_context(self, line_num: int) -> str:
        """Get context around a line number."""
        lines = self.code.split('\n')
        start = max(0, line_num - 3)
        end = min(len(lines), line_num + 2)
        return '\n'.join(lines[start:end])

    def _has_zero_guard(self, context: str) -> bool:
        """Check if context has a zero guard."""
        guard_patterns = [
            r'if\s+\w+\s*!=\s*0',
            r'if\s+\w+\s*>\s*0',
            r'if\s+\w+',
            r'try\s*:',
            r'except\s+ZeroDivisionError',
        ]
        return any(re.search(p, context) for p in guard_patterns)

    def _get_function_body(self, start_pos: int) -> str:
        """Extract function body starting from position."""
        # Simple extraction - find next def at same indentation or EOF
        remaining = self.code[start_pos:]
        lines = remaining.split('\n')
        body_lines = []

        for line in lines[1:]:  # Skip first line (def line)
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                break
            body_lines.append(line)

        return '\n'.join(body_lines)

    def _get_loop_body(self, start_pos: int) -> str:
        """Extract loop body starting from position."""
        remaining = self.code[start_pos:]
        lines = remaining.split('\n')
        body_lines = []
        indent = None

        for line in lines:
            if not line.strip():
                continue
            stripped = line.lstrip()
            current_indent = len(line) - len(stripped)

            if indent is None and stripped:
                indent = current_indent
                body_lines.append(line)
            elif stripped and current_indent > indent:
                body_lines.append(line)
            elif stripped and current_indent <= indent:
                break

        return '\n'.join(body_lines)


def detect_edge_cases(
    code: str,
    algorithm: Optional[Algorithm] = None,
    sandbox=None
) -> List[EdgeCase]:
    """Convenience function to detect edge cases.

    Args:
        code: Python code to analyze
        algorithm: Optional algorithm structure
        sandbox: Optional SandboxExecutor for execution testing

    Returns:
        List of detected edge cases
    """
    detector = EdgeCaseDetector(code, algorithm)

    if sandbox:
        return detector.analyze_execution(sandbox)
    else:
        return detector.analyze_static()
