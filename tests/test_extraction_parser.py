"""Tests for rule-based parser."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.extraction.parser import RuleBasedParser, parse_algorithm
from src.extraction.boundaries import (
    find_algorithm_name,
    extract_input_section,
    extract_output_section,
)
from src.extraction.schema import StepType

# Sample algorithms for testing
SAMPLE_SEQUENTIAL_SEARCH = """Algorithm: Sequential Search
Input: Array A[1..n], target value x
Output: Index of x in A, or -1 if not found

1. Initialize i = 1
2. While i ≤ n and A[i] ≠ x:
3. Increment i = i + 1
4. If i ≤ n:
5. Return i
6. Else:
7. Return -1"""

SAMPLE_BUBBLE_SORT = """Algorithm: Bubble Sort
Input: Array A[1..n]
Output: Sorted array A

1. For i from 1 to n-1:
2. For j from 1 to n-i:
3. If A[j] > A[j+1]:
4. Swap A[j] and A[j+1]
5. Return A"""


class TestBoundaryDetection:
    """Test algorithm boundary detection."""

    def test_find_algorithm_name(self):
        """Test extracting algorithm name from header."""
        name, line = find_algorithm_name("Algorithm: Test Search")
        assert name == "Test Search"
        assert line == 1

        name, line = find_algorithm_name("Procedure: Compute Sum")
        assert name == "Compute Sum"

    def test_extract_input_section(self):
        """Test extracting input section."""
        text = """Algorithm: Test
Input: x, y - integers
Output: sum
1. Step 1"""
        start, end, inputs = extract_input_section(text)
        assert start is not None
        assert len(inputs) > 0

    def test_extract_output_section(self):
        """Test extracting output section."""
        text = """Algorithm: Test
Input: x
Output: result
1. Step 1"""
        start, end, outputs = extract_output_section(text)
        assert start is not None
        assert len(outputs) > 0


class TestRuleBasedParser:
    """Test rule-based parser functionality."""

    def test_parse_algorithm_name(self):
        """Test parsing algorithm name."""
        algo = parse_algorithm("Algorithm: My Algorithm\n1. Step 1")
        assert algo.name == "My Algorithm"

    def test_parse_steps(self):
        """Test step extraction."""
        algo = parse_algorithm(SAMPLE_SEQUENTIAL_SEARCH)
        assert len(algo.steps) >= 5
        assert all(step.id > 0 for step in algo.steps)

    def test_step_classification(self):
        """Test step type classification."""
        algo = parse_algorithm(SAMPLE_SEQUENTIAL_SEARCH)

        # Should have assignment, loop, conditional, return steps
        types = [step.type for step in algo.steps]
        assert StepType.ASSIGNMENT in types
        assert StepType.LOOP_WHILE in types or StepType.LOOP_FOR in types
        assert StepType.CONDITIONAL in types
        assert StepType.RETURN in types

    def test_parse_inputs(self):
        """Test input extraction."""
        algo = parse_algorithm(SAMPLE_SEQUENTIAL_SEARCH)
        assert len(algo.inputs) >= 1

        # Check input names
        input_names = [inp["name"] for inp in algo.inputs]
        assert any("A" in name or "x" in name for name in input_names)

    def test_parse_outputs(self):
        """Test output extraction."""
        algo = parse_algorithm(SAMPLE_SEQUENTIAL_SEARCH)
        assert len(algo.outputs) >= 1


class TestStepDetails:
    """Test step detail extraction."""

    def test_loop_step_details(self):
        """Test loop step details."""
        algo = parse_algorithm(SAMPLE_BUBBLE_SORT)

        # Find for loop
        for_steps = [s for s in algo.steps if s.type == StepType.LOOP_FOR]
        assert len(for_steps) >= 1

        # Check iteration variable
        for step in for_steps:
            if step.iter_var:
                assert step.iter_var in ["i", "j"]

    def test_conditional_step_details(self):
        """Test conditional step details."""
        algo = parse_algorithm(SAMPLE_BUBBLE_SORT)

        # Find conditional
        if_steps = [s for s in algo.steps if s.type == StepType.CONDITIONAL]
        assert len(if_steps) >= 1

    def test_return_step_details(self):
        """Test return step details."""
        algo = parse_algorithm(SAMPLE_SEQUENTIAL_SEARCH)

        return_steps = [s for s in algo.steps if s.type == StepType.RETURN]
        assert len(return_steps) >= 1

    def test_variable_extraction(self):
        """Test variable extraction from steps."""
        algo = parse_algorithm("Algorithm: Test\n1. x = y + z")

        step = algo.steps[0]
        assert "x" in step.outputs
        assert "y" in step.inputs or "z" in step.inputs

    def test_line_references(self):
        """Test line reference preservation."""
        algo = parse_algorithm("Algorithm: Test\n1. Step 1\n2. Step 2")

        for step in algo.steps:
            assert len(step.line_refs) > 0
            assert all(isinstance(ref, int) for ref in step.line_refs)


class TestParserWithNotation:
    """Test parser with notation normalization."""

    def test_parses_subscripts(self):
        """Test that parser handles subscript notation."""
        text = """Algorithm: Matrix Access
Input: A_{i,j}
Output: element
1. x = A_{i,j}
2. Return x"""

        algo = parse_algorithm(text)
        assert algo.name == "Matrix Access"
        assert len(algo.steps) >= 1

    def test_parses_arrows(self):
        """Test that parser handles arrow notation."""
        text = """Algorithm: Arrow Test
1. x ← 5
2. y ← x + 1
3. Return y"""

        algo = parse_algorithm(text)
        assert len(algo.steps) >= 2
        # Variables should be extracted
        assert len(algo.steps[0].outputs) >= 1


class TestParserErrorHandling:
    """Test parser error handling."""

    def test_empty_text(self):
        """Test parsing empty text."""
        algo = parse_algorithm("")
        assert algo.name == "unnamed"
        assert len(algo.steps) == 0

    def test_no_steps(self):
        """Test parsing text without steps."""
        text = """Algorithm: No Steps
Input: x
Output: y"""
        algo = parse_algorithm(text)
        assert algo.name == "No Steps"
        assert len(algo.steps) == 0

    def test_unnamed_algorithm(self):
        """Test parsing algorithm without name."""
        text = """1. Step one
2. Step two"""
        algo = parse_algorithm(text)
        assert algo.name == "unnamed"
        assert len(algo.steps) >= 1


class TestParserIntegration:
    """Integration tests for the parser."""

    def test_complete_algorithm_extraction(self):
        """Test extracting complete algorithm with all features."""
        text = """Algorithm: Matrix Sum
Input: Matrix A[1..n, 1..m] - 2D array
Output: Sum of all elements

1. Initialize sum = 0
2. For i from 1 to n:
3. For j from 1 to m:
4. sum ← sum + A_{i,j}
5. Return sum"""

        algo = parse_algorithm(text)

        # Check name
        assert algo.name == "Matrix Sum"

        # Check inputs/outputs
        assert len(algo.inputs) >= 1
        assert len(algo.outputs) >= 1

        # Check steps
        assert len(algo.steps) >= 3

        # Check for loops
        loop_steps = [s for s in algo.steps if s.type == StepType.LOOP_FOR]
        assert len(loop_steps) >= 1

        # Check assignment
        assign_steps = [s for s in algo.steps if s.type == StepType.ASSIGNMENT]
        assert len(assign_steps) >= 1

        # Check return
        return_steps = [s for s in algo.steps if s.type == StepType.RETURN]
        assert len(return_steps) >= 1


class TestStepClassificationEdgeCases:
    """Test edge cases in step classification."""

    def test_call_classification(self):
        """Test function call step classification."""
        algo = parse_algorithm("Algorithm: Test\n1. Call helper(x)")
        # Should detect as call or assignment
        assert algo.steps[0].type in [StepType.CALL, StepType.ASSIGNMENT, StepType.COMMENT]

    def test_comment_classification(self):
        """Test comment step classification."""
        algo = parse_algorithm("Algorithm: Test\n1. // This is a comment")
        step = algo.steps[0]
        # Should be classified as comment or assignment
        assert step.type in [StepType.COMMENT, StepType.ASSIGNMENT]

    def test_assignment_variations(self):
        """Test various assignment patterns."""
        text = """Algorithm: Assignments
1. x = 1
2. y ← 2
3. z gets 3
4. w is set to 4"""
        algo = parse_algorithm(text)
        # All should be classified as assignments
        for step in algo.steps:
            assert step.type == StepType.ASSIGNMENT


def run_all_tests():
    """Run all tests and report results."""
    test_classes = [
        TestBoundaryDetection,
        TestRuleBasedParser,
        TestStepDetails,
        TestParserWithNotation,
        TestParserErrorHandling,
        TestParserIntegration,
        TestStepClassificationEdgeCases,
    ]

    passed = 0
    failed = 0

    for test_class in test_classes:
        instance = test_class()
        methods = [m for m in dir(instance) if m.startswith('test_')]

        for method_name in methods:
            try:
                method = getattr(instance, method_name)
                method()
                print(f"✓ {test_class.__name__}.{method_name}")
                passed += 1
            except Exception as e:
                print(f"✗ {test_class.__name__}.{method_name}: {e}")
                failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
