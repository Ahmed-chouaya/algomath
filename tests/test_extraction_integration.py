"""Integration tests for extraction workflow."""
import pytest
import json
from pathlib import Path

from src.extraction import (
    HybridExtractor,
    Algorithm,
    Step,
    StepType,
    ReviewInterface,
    validate_algorithm,
    categorize_error,
    ParseError,
    algorithm_to_json,
    algorithm_from_json,
)


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


class TestEndToEndExtraction:
    """Test complete extraction workflow."""

    def test_extract_sequential_search(self):
        """Test extracting sequential search algorithm."""
        extractor = HybridExtractor()
        result = extractor.extract(SAMPLE_SEQUENTIAL_SEARCH, prefer_llm=False)

        assert result.success
        assert result.method == "rule_based"
        assert result.algorithm.name == "Sequential Search"

        # Check inputs/outputs
        assert len(result.algorithm.inputs) >= 1
        assert len(result.algorithm.outputs) >= 1

        # Check steps
        assert len(result.algorithm.steps) >= 5

        # Validate
        validation = validate_algorithm(result.algorithm)
        assert validation.is_valid

    def test_extract_bubble_sort(self):
        """Test extracting bubble sort with nested loops."""
        extractor = HybridExtractor()
        result = extractor.extract(SAMPLE_BUBBLE_SORT, prefer_llm=False)

        assert result.success
        assert result.algorithm.name == "Bubble Sort"

        # Check for loops
        loop_steps = [s for s in result.algorithm.steps
                      if s.type in (StepType.LOOP_FOR, StepType.LOOP_WHILE)]
        assert len(loop_steps) >= 2

    def test_review_and_approve_workflow(self):
        """Test complete review and approval workflow."""
        extractor = HybridExtractor()
        result = extractor.extract(SAMPLE_SEQUENTIAL_SEARCH, prefer_llm=False)

        # Create review interface
        review = ReviewInterface(result.algorithm)

        # Edit a step
        success, errors = review.edit_step(1, {"description": "Set i = 1"})
        assert success

        # Validate
        validation = validate_algorithm(review.working)
        assert validation.is_valid

        # Approve
        final = review.approve()
        assert final.steps[0].description == "Set i = 1"


class TestValidationAndErrors:
    """Test validation and error handling."""

    def test_detects_missing_steps(self):
        """Test validation catches empty algorithm."""
        algo = Algorithm(name="empty", steps=[])
        result = validate_algorithm(algo)

        assert not result.is_valid
        assert any("no steps" in str(e).lower() for e in result.errors)

    def test_detects_duplicate_step_ids(self):
        """Test validation catches duplicate IDs."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1"),
            Step(id=1, type=StepType.RETURN, description="return x"),
        ])
        result = validate_algorithm(algo)

        assert not result.is_valid
        assert any("duplicate" in str(e).lower() for e in result.errors)

    def test_detects_undefined_variable(self):
        """Test variable flow detection."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.RETURN, description="return y", inputs=["y"]),
        ])
        result = validate_algorithm(algo)

        # Should have warning about undefined variable
        assert any("y" in w for w in result.warnings)

    def test_categorize_parse_error(self):
        """Test error categorization for parse errors."""
        error = categorize_error("unmatched parenthesis at line 5", 5)
        assert isinstance(error, ParseError)
        assert error.line_number == 5


class TestJSONSerialization:
    """Test algorithm JSON serialization."""

    def test_serialize_to_json(self):
        """Test converting algorithm to JSON."""
        algo = Algorithm(
            name="Sum",
            description="Sum array elements",
            inputs=[{"name": "A", "type": "array"}],
            outputs=[{"name": "sum", "type": "float"}],
            steps=[
                Step(id=1, type=StepType.ASSIGNMENT, description="s = 0",
                     outputs=["s"], line_refs=[1]),
                Step(id=2, type=StepType.RETURN, description="return s",
                     inputs=["s"], line_refs=[2]),
            ]
        )

        json_str = algorithm_to_json(algo)

        assert "Sum" in json_str
        assert "steps" in json_str
        assert isinstance(json.loads(json_str), dict)

    def test_round_trip_serialization(self):
        """Test JSON round-trip preserves data."""
        algo = Algorithm(
            name="Test",
            steps=[
                Step(id=1, type=StepType.ASSIGNMENT, description="x = 1"),
            ]
        )

        json_str = algorithm_to_json(algo)
        restored = algorithm_from_json(json_str)

        assert restored.name == algo.name
        assert len(restored.steps) == len(algo.steps)
        assert restored.steps[0].type == StepType.ASSIGNMENT


class TestWorkflowIntegration:
    """Test integration with extraction workflow."""

    def test_run_extraction_stubs(self, tmp_path):
        """Test extraction workflow function."""
        # This test checks the stub behavior
        # Full integration would require ContextManager setup

        from src.workflows.extract import run_extraction

        # Mock context manager
        class MockContext:
            def __init__(self):
                self.text = None
                self.steps = None

            def save_text(self, text):
                self.text = text

            def save_steps(self, steps):
                self.steps = steps

        context = MockContext()

        result = run_extraction(
            context,
            text=SAMPLE_SEQUENTIAL_SEARCH,
            name="test_search"
        )

        assert result['status'] == 'extraction_complete'
        assert result['steps_extracted'] > 0
        assert context.text is not None
        assert context.steps is not None


class TestHybridExtraction:
    """Test hybrid extraction with fallback."""

    def test_rule_based_extraction(self):
        """Test rule-based extraction path."""
        extractor = HybridExtractor()

        text = """
        Algorithm: Test
        1. Set x = 1
        2. Return x
        """

        result = extractor.extract(text, name="Test", prefer_llm=False)

        assert result.success
        assert result.method == "rule_based"
        assert len(result.algorithm.steps) >= 2

    def test_extraction_with_validation(self):
        """Test extraction includes validation."""
        extractor = HybridExtractor()

        text = """
        Algorithm: Valid
        1. Initialize counter = 0
        2. While counter < 10:
        3. Increment counter
        4. Return counter
        """

        result = extractor.extract(text)
        validation = validate_algorithm(result.algorithm)

        # May have warnings but should be structurally valid
        assert validation.is_valid or len(validation.errors) == 0


class TestReviewOperations:
    """Test review interface operations."""

    def test_delete_step(self):
        """Test step deletion."""
        algo = Algorithm(name="Test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1"),
            Step(id=2, type=StepType.RETURN, description="return x"),
        ])

        review = ReviewInterface(algo)
        review.delete_step(1)

        assert len(review.working.steps) == 1
        assert review.working.steps[0].id == 2

    def test_add_step(self):
        """Test adding new step."""
        algo = Algorithm(name="Test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1"),
        ])

        review = ReviewInterface(algo)
        new_id = review.add_step({
            "type": "return",
            "description": "return x"
        })

        assert new_id == 2
        assert len(review.working.steps) == 2

    def test_reorder_steps(self):
        """Test step reordering."""
        algo = Algorithm(name="Test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1"),
            Step(id=2, type=StepType.ASSIGNMENT, description="y = 2"),
            Step(id=3, type=StepType.RETURN, description="return x + y"),
        ])

        review = ReviewInterface(algo)
        review.reorder_steps([3, 1, 2])

        assert review.working.steps[0].id == 3
        assert review.working.steps[1].id == 1
        assert review.working.steps[2].id == 2

    def test_reset_changes(self):
        """Test reset functionality."""
        algo = Algorithm(name="Test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1"),
        ])

        review = ReviewInterface(algo)
        review.edit_step(1, {"description": "x = 2"})
        assert review.working.steps[0].description == "x = 2"

        review.reset()
        assert review.working.steps[0].description == "x = 1"
