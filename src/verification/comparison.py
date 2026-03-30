"""Expected results comparison module for AlgoMath.

Per VER-02: Compare output against expected results.
Implements decisions D-09, D-10, D-11, D-12 from 05-CONTEXT.md.
"""

import difflib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class ComparisonStatus(Enum):
    """Comparison status enumeration.

    MATCH: Expected and actual values match completely
    MISMATCH: Expected and actual values differ
    PARTIAL: Some fields match, some differ (for structured data)
    NOT_PROVIDED: No expected value was provided
    """
    MATCH = "match"
    MISMATCH = "mismatch"
    PARTIAL = "partial"
    NOT_PROVIDED = "not_provided"


@dataclass
class ComparisonResult:
    """Result of comparing expected vs actual output.

    Per D-11: Shows expected vs actual with highlight of differences.

    Attributes:
        status: Overall comparison status
        expected: The expected value (what user provided)
        actual: The actual value (what execution produced)
        diff: Unified diff string showing differences
        match_percentage: Float from 0.0 to 1.0 indicating match quality
        differences: List of per-field differences for structured data
    """
    status: ComparisonStatus
    expected: Any
    actual: Any
    diff: Optional[str] = None
    match_percentage: float = 0.0
    differences: List[Dict[str, Any]] = field(default_factory=list)

    def format_inline(self) -> str:
        """Format comparison result for inline display per D-11.

        Shows expected vs actual with markdown formatting.
        For visual distinction: green (match) / red (differ) indicators.

        Returns:
            Formatted string with clear visual indicators
        """
        if self.status == ComparisonStatus.MATCH:
            return f"✅ **Match**: Expected and actual values are identical."
        elif self.status == ComparisonStatus.NOT_PROVIDED:
            return "⚠️ **No expected value provided**: Cannot perform comparison."
        elif self.status == ComparisonStatus.MISMATCH:
            lines = [
                f"❌ **Mismatch**: Expected and actual values differ.",
                f"",
                f"**Expected:**",
                f"```",
                f"{self._format_value(self.expected)}",
                f"```",
                f"",
                f"**Actual:**",
                f"```",
                f"{self._format_value(self.actual)}",
                f"```",
            ]
            if self.diff:
                lines.extend([
                    f"",
                    f"**Differences:**",
                    f"```diff",
                    f"{self.diff}",
                    f"```",
                ])
            return "\n".join(lines)
        elif self.status == ComparisonStatus.PARTIAL:
            return f"⚡ **Partial Match**: {self.match_percentage*100:.1f}% of fields match."
        else:
            return f"Comparison result: {self.status.value}"

    def _format_value(self, value: Any) -> str:
        """Format a value for display."""
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value, indent=2, default=str)
        except:
            return str(value)


class OutputComparator:
    """Comparator for expected vs actual output.

    Performs comparison with support for:
    - Exact string matching
    - Numeric tolerance (for floating point comparisons)
    - Multi-line string diff with line numbers
    - Structured data comparison (dicts, lists)

    Per D-11: Shows unified diff format for text comparison.
    Per D-12: Optional feature - user can skip comparison.
    """

    def __init__(self, tolerance: float = 0.001):
        """Initialize comparator with tolerance for numeric comparisons.

        Args:
            tolerance: Maximum difference allowed for float equality (default 0.001)
        """
        self.tolerance = tolerance

    def compare(self, expected: Any, actual: Any) -> ComparisonResult:
        """Compare expected vs actual values.

        Args:
            expected: The expected value (from user)
            actual: The actual value (from execution)

        Returns:
            ComparisonResult with status and diff information
        """
        # Handle both None - they match
        if expected is None and actual is None:
            return ComparisonResult(
                status=ComparisonStatus.MATCH,
                expected=expected,
                actual=actual,
                match_percentage=1.0
            )

        # Handle None expected (no expected provided)
        if expected is None:
            return ComparisonResult(
                status=ComparisonStatus.NOT_PROVIDED,
                expected=expected,
                actual=actual,
                match_percentage=0.0
            )

        # Handle type mismatch
        if type(expected) != type(actual) and not (isinstance(expected, (int, float)) and isinstance(actual, (int, float))):
            return ComparisonResult(
                status=ComparisonStatus.MISMATCH,
                expected=expected,
                actual=actual,
                diff=f"Type mismatch: expected {type(expected).__name__}, got {type(actual).__name__}",
                match_percentage=0.0
            )

        # Compare based on type
        if isinstance(expected, dict):
            return self._compare_structured(expected, actual)
        elif isinstance(expected, list):
            return self._compare_list(expected, actual)
        elif isinstance(expected, (int, float)):
            return self._compare_numeric(expected, actual)
        elif isinstance(expected, str):
            return self._compare_strings(expected, actual)
        else:
            # Generic comparison for other types
            if expected == actual:
                return ComparisonResult(
                    status=ComparisonStatus.MATCH,
                    expected=expected,
                    actual=actual,
                    match_percentage=1.0
                )
            else:
                return ComparisonResult(
                    status=ComparisonStatus.MISMATCH,
                    expected=expected,
                    actual=actual,
                    diff=f"Expected: {expected}\nActual: {actual}",
                    match_percentage=0.0
                )

    def _compare_numeric(self, expected: Union[int, float], actual: Union[int, float]) -> ComparisonResult:
        """Compare numeric values with tolerance.

        Per D-11: Default tolerance of 0.001 for floating point comparisons.

        Args:
            expected: Expected numeric value
            actual: Actual numeric value

        Returns:
            ComparisonResult with numeric comparison result
        """
        if isinstance(expected, int) and isinstance(actual, int):
            if expected == actual:
                return ComparisonResult(
                    status=ComparisonStatus.MATCH,
                    expected=expected,
                    actual=actual,
                    match_percentage=1.0
                )
            else:
                return ComparisonResult(
                    status=ComparisonStatus.MISMATCH,
                    expected=expected,
                    actual=actual,
                    diff=f"- {expected}\n+ {actual}",
                    match_percentage=0.0
                )
        else:
            # Float comparison with tolerance
            diff = abs(float(expected) - float(actual))
            if diff <= self.tolerance:
                return ComparisonResult(
                    status=ComparisonStatus.MATCH,
                    expected=expected,
                    actual=actual,
                    match_percentage=1.0 - (diff / max(abs(float(expected)), 1.0))
                )
            else:
                return ComparisonResult(
                    status=ComparisonStatus.MISMATCH,
                    expected=expected,
                    actual=actual,
                    diff=f"- {expected}\n+ {actual} (diff: {diff:.6f}, tolerance: {self.tolerance})",
                    match_percentage=max(0.0, 1.0 - (diff / max(abs(float(expected)), 1.0)))
                )

    def _compare_strings(self, expected: str, actual: str) -> ComparisonResult:
        """Compare string values with unified diff.

        Per D-11: Use unified diff format for text comparison.
        Per D-11: Show "expected" vs "actual" with clear labels.

        Args:
            expected: Expected string value
            actual: Actual string value

        Returns:
            ComparisonResult with string comparison result
        """
        if expected == actual:
            return ComparisonResult(
                status=ComparisonStatus.MATCH,
                expected=expected,
                actual=actual,
                match_percentage=1.0
            )

        # Generate unified diff
        expected_lines = expected.splitlines(keepends=True)
        actual_lines = actual.splitlines(keepends=True)

        # Handle missing newlines at end
        if expected_lines and not expected_lines[-1].endswith('\n'):
            expected_lines[-1] += '\n'
        if actual_lines and not actual_lines[-1].endswith('\n'):
            actual_lines[-1] += '\n'

        diff = difflib.unified_diff(
            expected_lines,
            actual_lines,
            fromfile='expected',
            tofile='actual',
            lineterm=''
        )
        diff_str = ''.join(diff)

        # Calculate match percentage (simple character-based)
        if len(expected) == 0 and len(actual) == 0:
            match_pct = 1.0
        elif len(expected) == 0 or len(actual) == 0:
            match_pct = 0.0
        else:
            # Use difflib.SequenceMatcher for similarity ratio
            matcher = difflib.SequenceMatcher(None, expected, actual)
            match_pct = matcher.ratio()

        return ComparisonResult(
            status=ComparisonStatus.MISMATCH,
            expected=expected,
            actual=actual,
            diff=diff_str if diff_str else None,
            match_percentage=match_pct,
            differences=[]
        )

    def _compare_structured(self, expected: Dict[str, Any], actual: Dict[str, Any]) -> ComparisonResult:
        """Compare structured data (dictionaries).

        Args:
            expected: Expected dictionary
            actual: Actual dictionary

        Returns:
            ComparisonResult with structured comparison result
        """
        differences = []
        matched_keys = 0
        total_keys = len(expected)

        for key in expected:
            if key not in actual:
                differences.append({
                    'field': key,
                    'expected': expected[key],
                    'actual': None,
                    'status': 'missing_in_actual'
                })
            else:
                # Recursively compare values
                sub_result = self.compare(expected[key], actual[key])
                if sub_result.status != ComparisonStatus.MATCH:
                    differences.append({
                        'field': key,
                        'expected': expected[key],
                        'actual': actual[key],
                        'status': sub_result.status.value,
                        'diff': sub_result.diff
                    })
                else:
                    matched_keys += 1

        # Check for extra keys in actual
        for key in actual:
            if key not in expected:
                differences.append({
                    'field': key,
                    'expected': None,
                    'actual': actual[key],
                    'status': 'extra_in_actual'
                })

        if len(differences) == 0:
            return ComparisonResult(
                status=ComparisonStatus.MATCH,
                expected=expected,
                actual=actual,
                match_percentage=1.0
            )
        elif matched_keys > 0:
            total_fields = len(set(expected.keys()) | set(actual.keys()))
            match_pct = matched_keys / total_fields if total_fields > 0 else 0.0
            return ComparisonResult(
                status=ComparisonStatus.PARTIAL,
                expected=expected,
                actual=actual,
                match_percentage=match_pct,
                differences=differences
            )
        else:
            return ComparisonResult(
                status=ComparisonStatus.MISMATCH,
                expected=expected,
                actual=actual,
                match_percentage=0.0,
                differences=differences
            )

    def _compare_list(self, expected: List[Any], actual: List[Any]) -> ComparisonResult:
        """Compare list values.

        Args:
            expected: Expected list
            actual: Actual list

        Returns:
            ComparisonResult with list comparison result
        """
        if expected == actual:
            return ComparisonResult(
                status=ComparisonStatus.MATCH,
                expected=expected,
                actual=actual,
                match_percentage=1.0
            )

        differences = []
        max_len = max(len(expected), len(actual))
        matches = 0

        for i in range(max_len):
            if i < len(expected) and i < len(actual):
                sub_result = self.compare(expected[i], actual[i])
                if sub_result.status != ComparisonStatus.MATCH:
                    differences.append({
                        'index': i,
                        'expected': expected[i],
                        'actual': actual[i],
                        'status': sub_result.status.value
                    })
                else:
                    matches += 1
            elif i >= len(expected):
                differences.append({
                    'index': i,
                    'expected': None,
                    'actual': actual[i],
                    'status': 'extra_element'
                })
            else:
                differences.append({
                    'index': i,
                    'expected': expected[i],
                    'actual': None,
                    'status': 'missing_element'
                })

        match_pct = matches / max_len if max_len > 0 else 0.0

        if len(differences) == 0:
            return ComparisonResult(
                status=ComparisonStatus.MATCH,
                expected=expected,
                actual=actual,
                match_percentage=1.0
            )
        elif matches > 0:
            return ComparisonResult(
                status=ComparisonStatus.PARTIAL,
                expected=expected,
                actual=actual,
                match_percentage=match_pct,
                differences=differences
            )
        else:
            return ComparisonResult(
                status=ComparisonStatus.MISMATCH,
                expected=expected,
                actual=actual,
                match_percentage=match_pct,
                differences=differences
            )

    def interactive_prompt(self) -> Optional[Any]:
        """Prompt user for expected value per D-09.

        Per D-09: Ask "Do you have expected results to compare?"
        Per D-10: Support both inline value and file path.

        Returns:
            Parsed expected value or None if skipped
        """
        # This method is a placeholder for interactive prompting
        # In a real implementation, this would use input() or a GUI
        # For now, returns None indicating no expected value provided
        return None


def compare_outputs(expected: Any, actual: Any, tolerance: float = 0.001) -> ComparisonResult:
    """High-level function to compare expected vs actual outputs.

    Args:
        expected: The expected value
        actual: The actual value
        tolerance: Numeric tolerance for float comparisons (default 0.001)

    Returns:
        ComparisonResult with comparison status and diff
    """
    comparator = OutputComparator(tolerance=tolerance)
    return comparator.compare(expected, actual)


def prompt_for_expected() -> Optional[Any]:
    """Prompt user for expected results per D-09, D-10.

    Asks user if they have expected results to compare.
    Supports inline value or file path input.

    Per D-09: "Do you have expected results to compare?"
    Per D-10: Support both inline value and file path.

    Returns:
        Parsed expected value or None if skipped
    """
    # Placeholder implementation - would integrate with UI in real use
    # Returns None to indicate no expected value was provided
    return None


__all__ = [
    'ComparisonStatus',
    'ComparisonResult',
    'OutputComparator',
    'compare_outputs',
    'prompt_for_expected',
]
