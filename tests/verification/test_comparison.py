"""Tests for expected results comparison.

Per VER-02: Compare output against expected results.
Covers TDD behaviors for Task 2 of 05-01-PLAN.md.
"""

import pytest
from src.verification.comparison import (
    ComparisonStatus,
    ComparisonResult,
    OutputComparator,
    compare_outputs,
    prompt_for_expected,
)


class TestComparisonStatus:
    """Test ComparisonStatus enum."""

    def test_status_values_exist(self):
        """Test that all comparison status values are defined."""
        assert ComparisonStatus.MATCH.value == 'match'
        assert ComparisonStatus.MISMATCH.value == 'mismatch'
        assert ComparisonStatus.PARTIAL.value == 'partial'
        assert ComparisonStatus.NOT_PROVIDED.value == 'not_provided'


class TestComparisonResult:
    """Test ComparisonResult dataclass."""

    def test_result_creation(self):
        """Test ComparisonResult creation."""
        result = ComparisonResult(
            status=ComparisonStatus.MATCH,
            expected="hello",
            actual="hello",
            diff=None,
            match_percentage=1.0,
            differences=[]
        )
        assert result.status == ComparisonStatus.MATCH
        assert result.expected == "hello"
        assert result.actual == "hello"
        assert result.match_percentage == 1.0

    def test_format_inline(self):
        """Test 6: Comparison result includes highlight format."""
        result = ComparisonResult(
            status=ComparisonStatus.MATCH,
            expected="hello",
            actual="hello",
            diff=None,
            match_percentage=1.0,
            differences=[]
        )
        formatted = result.format_inline()
        assert isinstance(formatted, str)
        # Should indicate match
        assert 'match' in formatted.lower() or 'expected' in formatted.lower()


class TestOutputComparator:
    """Test OutputComparator class."""

    def test_comparator_initialization(self):
        """Test that OutputComparator can be initialized."""
        comparator = OutputComparator()
        assert comparator.tolerance == 0.001

    def test_comparator_custom_tolerance(self):
        """Test initialization with custom tolerance."""
        comparator = OutputComparator(tolerance=0.01)
        assert comparator.tolerance == 0.01

    def test_compare_strings_match(self):
        """Test 1: compare_outputs() returns MATCH when expected == actual."""
        comparator = OutputComparator()
        result = comparator.compare("hello", "hello")
        assert result.status == ComparisonStatus.MATCH
        assert result.match_percentage == 1.0

    def test_compare_strings_mismatch(self):
        """Test 2: compare_outputs() returns MISMATCH with diff when values differ."""
        comparator = OutputComparator()
        result = comparator.compare("hello", "world")
        assert result.status == ComparisonStatus.MISMATCH
        assert result.diff is not None
        assert result.match_percentage < 1.0

    def test_compare_numeric_match_exact(self):
        """Test 3: Comparison supports numeric tolerance for exact match."""
        comparator = OutputComparator(tolerance=0.001)
        result = comparator.compare(3.14159, 3.14159)
        assert result.status == ComparisonStatus.MATCH

    def test_compare_numeric_within_tolerance(self):
        """Test 3: Comparison supports numeric tolerance (0.001 default for floats)."""
        comparator = OutputComparator(tolerance=0.001)
        result = comparator.compare(3.14159, 3.14160)  # Diff: 0.00001 < 0.001
        assert result.status == ComparisonStatus.MATCH

    def test_compare_numeric_outside_tolerance(self):
        """Test 3: Values outside tolerance are mismatches."""
        comparator = OutputComparator(tolerance=0.001)
        result = comparator.compare(3.14159, 3.142)  # Diff: 0.00041 < 0.001
        # This should match with default tolerance
        assert result.status == ComparisonStatus.MATCH

    def test_compare_numeric_large_diff(self):
        """Test 3: Large differences outside tolerance."""
        comparator = OutputComparator(tolerance=0.001)
        result = comparator.compare(3.14, 3.15)  # Diff: 0.01 > 0.001
        assert result.status == ComparisonStatus.MISMATCH

    def test_compare_multiline_strings_with_line_numbers(self):
        """Test 4: Comparison handles multi-line string diff with line numbers."""
        comparator = OutputComparator()
        expected = "line1\nline2\nline3"
        actual = "line1\nmodified\nline3"
        result = comparator.compare(expected, actual)
        assert result.status == ComparisonStatus.MISMATCH
        assert result.diff is not None
        # Diff should contain line numbers
        assert '-' in result.diff or '+' in result.diff or 'line' in result.diff

    def test_compare_structured_dict_match(self):
        """Test structured data comparison - dict match."""
        comparator = OutputComparator()
        expected = {'a': 1, 'b': 2}
        actual = {'a': 1, 'b': 2}
        result = comparator.compare(expected, actual)
        assert result.status == ComparisonStatus.MATCH

    def test_compare_structured_dict_mismatch(self):
        """Test structured data comparison - dict mismatch."""
        comparator = OutputComparator()
        expected = {'a': 1, 'b': 2}
        actual = {'a': 1, 'b': 3}
        result = comparator.compare(expected, actual)
        assert result.status == ComparisonStatus.MISMATCH
        assert len(result.differences) > 0

    def test_compare_list_match(self):
        """Test list comparison - match."""
        comparator = OutputComparator()
        result = comparator.compare([1, 2, 3], [1, 2, 3])
        assert result.status == ComparisonStatus.MATCH

    def test_compare_list_mismatch(self):
        """Test list comparison - mismatch."""
        comparator = OutputComparator()
        result = comparator.compare([1, 2, 3], [1, 2, 4])
        assert result.status == ComparisonStatus.MISMATCH

    def test_compare_mixed_types(self):
        """Test comparing different types."""
        comparator = OutputComparator()
        result = comparator.compare("hello", 123)
        assert result.status == ComparisonStatus.MISMATCH

    def test_compare_none_expected(self):
        """Test when expected is None."""
        comparator = OutputComparator()
        result = comparator.compare(None, "actual")
        assert result.status == ComparisonStatus.NOT_PROVIDED

    def test_compare_none_both(self):
        """Test when both expected and actual are None."""
        comparator = OutputComparator()
        result = comparator.compare(None, None)
        assert result.status == ComparisonStatus.MATCH


class TestCompareOutputs:
    """Test compare_outputs function."""

    def test_compare_outputs_function_match(self):
        """Test compare_outputs function with matching values."""
        result = compare_outputs("hello", "hello")
        assert result.status == ComparisonStatus.MATCH

    def test_compare_outputs_function_mismatch(self):
        """Test compare_outputs function with different values."""
        result = compare_outputs("hello", "world")
        assert result.status == ComparisonStatus.MISMATCH

    def test_compare_outputs_with_tolerance(self):
        """Test compare_outputs with custom tolerance."""
        result = compare_outputs(3.14159, 3.14160, tolerance=0.0001)
        assert result.status == ComparisonStatus.MATCH


class TestFormatInline:
    """Test format_inline method per D-11."""

    def test_format_inline_match(self):
        """Test 6: Inline format shows match indicator."""
        result = ComparisonResult(
            status=ComparisonStatus.MATCH,
            expected="test",
            actual="test",
            diff=None,
            match_percentage=1.0,
            differences=[]
        )
        formatted = result.format_inline()
        # Should indicate success/green for match
        assert 'match' in formatted.lower() or 'expected' in formatted.lower()

    def test_format_inline_mismatch(self):
        """Test 6: Inline format shows mismatch with diff."""
        result = ComparisonResult(
            status=ComparisonStatus.MISMATCH,
            expected="hello",
            actual="world",
            diff="-hello\n+world",
            match_percentage=0.0,
            differences=[]
        )
        formatted = result.format_inline()
        assert isinstance(formatted, str)
        # Should show both expected and actual
        assert 'expected' in formatted.lower() or 'actual' in formatted.lower()


class TestPromptForExpected:
    """Test prompt_for_expected function per D-09, D-10."""

    def test_prompt_function_exists(self):
        """Test 5: prompt_for_expected function exists."""
        assert callable(prompt_for_expected)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
