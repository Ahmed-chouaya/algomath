"""Tests for review interface."""
import pytest
from src.extraction.review import ReviewInterface, validate_step_edit, apply_edits
from src.extraction.schema import Algorithm, Step, StepType


class TestReviewInterface:
    """Test review interface functionality."""

    def test_create_review_interface(self):
        """Test creating review interface."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1")
        ])
        review = ReviewInterface(algo)

        data = review.get_side_by_side()
        assert "original_text" in data
        assert "steps" in data
        assert len(data["steps"]) == 1

    def test_edit_step_description(self):
        """Test editing step description."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1")
        ])
        review = ReviewInterface(algo)

        success, errors = review.edit_step(1, {"description": "y = 2"})
        assert success
        assert review.working.steps[0].description == "y = 2"

    def test_edit_step_type(self):
        """Test editing step type."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1")
        ])
        review = ReviewInterface(algo)

        success, errors = review.edit_step(1, {"type": "return"})
        assert success
        assert review.working.steps[0].type == StepType.RETURN

    def test_edit_nonexistent_step(self):
        """Test editing non-existent step."""
        algo = Algorithm(name="test", steps=[])
        review = ReviewInterface(algo)

        success, errors = review.edit_step(1, {"description": "test"})
        assert not success
        assert "not found" in str(errors)

    def test_reorder_step(self):
        """Test reordering steps."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1"),
            Step(id=2, type=StepType.RETURN, description="return x")
        ])
        review = ReviewInterface(algo)

        success, msg = review.reorder_step(2, 1)
        assert success
        assert review.working.steps[0].description == "return x"

    def test_reorder_to_same_position(self):
        """Test reordering to same position."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1")
        ])
        review = ReviewInterface(algo)

        success, msg = review.reorder_step(1, 1)
        assert success

    def test_delete_step(self):
        """Test deleting a step."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1"),
            Step(id=2, type=StepType.RETURN, description="return x")
        ])
        review = ReviewInterface(algo)

        success, msg = review.delete_step(1)
        assert success
        assert len(review.working.steps) == 1
        assert review.working.steps[0].id == 1  # Renumbered

    def test_delete_nonexistent_step(self):
        """Test deleting non-existent step."""
        algo = Algorithm(name="test", steps=[])
        review = ReviewInterface(algo)

        success, msg = review.delete_step(1)
        assert not success
        assert "not found" in msg

    def test_add_step(self):
        """Test adding a new step."""
        algo = Algorithm(name="test", steps=[])
        review = ReviewInterface(algo)

        success, result = review.add_step(1, {
            "type": "assignment",
            "description": "x = 1",
            "inputs": [],
            "outputs": ["x"]
        })
        assert success
        assert len(review.working.steps) == 1
        assert review.working.steps[0].id == 1

    def test_add_step_at_end(self):
        """Test adding step at end."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1")
        ])
        review = ReviewInterface(algo)

        success, result = review.add_step(-1, {
            "type": "return",
            "description": "return x",
            "inputs": ["x"],
            "outputs": []
        })
        assert success
        assert len(review.working.steps) == 2


class TestStepValidation:
    """Test step edit validation."""

    def test_valid_step_edit(self):
        """Test validation of valid edits."""
        step = Step(id=1, type=StepType.ASSIGNMENT, description="x = 1")
        is_valid, errors = validate_step_edit(step, {"description": "y = 2"})
        assert is_valid
        assert len(errors) == 0

    def test_invalid_step_type(self):
        """Test rejection of invalid step type."""
        step = Step(id=1, type=StepType.ASSIGNMENT, description="x = 1")
        is_valid, errors = validate_step_edit(step, {"type": "invalid_type"})
        assert not is_valid
        assert any("Invalid" in e for e in errors)

    def test_empty_description(self):
        """Test rejection of empty description."""
        step = Step(id=1, type=StepType.ASSIGNMENT, description="x = 1")
        is_valid, errors = validate_step_edit(step, {"description": ""})
        assert not is_valid
        assert any("empty" in e.lower() for e in errors)

    def test_invalid_step_id(self):
        """Test rejection of invalid step ID."""
        step = Step(id=1, type=StepType.ASSIGNMENT, description="x = 1")
        is_valid, errors = validate_step_edit(step, {"id": -1})
        assert not is_valid
        assert any("positive" in e.lower() for e in errors)

    def test_invalid_inputs_type(self):
        """Test rejection of non-list inputs."""
        step = Step(id=1, type=StepType.ASSIGNMENT, description="x = 1")
        is_valid, errors = validate_step_edit(step, {"inputs": "not a list"})
        assert not is_valid

    def test_invalid_outputs_type(self):
        """Test rejection of non-list outputs."""
        step = Step(id=1, type=StepType.ASSIGNMENT, description="x = 1")
        is_valid, errors = validate_step_edit(step, {"outputs": "not a list"})
        assert not is_valid


class TestApplyEdits:
    """Test applying multiple edits."""

    def test_apply_single_edit(self):
        """Test applying a single edit."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1")
        ])

        edits = [
            {"action": "edit", "step_id": 1, "edits": {"description": "y = 2"}}
        ]

        result = apply_edits(algo, edits)
        assert result.steps[0].description == "y = 2"

    def test_apply_multiple_edits(self):
        """Test applying multiple edits."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1"),
            Step(id=2, type=StepType.RETURN, description="return x")
        ])

        edits = [
            {"action": "edit", "step_id": 1, "edits": {"description": "y = 1"}},
            {"action": "edit", "step_id": 2, "edits": {"description": "return y"}}
        ]

        result = apply_edits(algo, edits)
        assert result.steps[0].description == "y = 1"
        assert result.steps[1].description == "return y"

    def test_apply_delete_edit(self):
        """Test applying delete edit."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1"),
            Step(id=2, type=StepType.RETURN, description="return x")
        ])

        edits = [{"action": "delete", "step_id": 1}]

        result = apply_edits(algo, edits)
        assert len(result.steps) == 1

    def test_apply_add_edit(self):
        """Test applying add edit."""
        algo = Algorithm(name="test", steps=[])

        edits = [
            {"action": "add", "position": 1, "step_data": {
                "type": "assignment",
                "description": "x = 1"
            }}
        ]

        result = apply_edits(algo, edits)
        assert len(result.steps) == 1

    def test_apply_reorder_edit(self):
        """Test applying reorder edit."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="first"),
            Step(id=2, type=StepType.RETURN, description="second")
        ])

        edits = [{"action": "reorder", "step_id": 2, "new_position": 1}]

        result = apply_edits(algo, edits)
        assert result.steps[0].description == "second"


class TestReviewInterfaceReset:
    """Test review interface reset."""

    def test_reset_to_original(self):
        """Test resetting to original algorithm."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1")
        ])
        review = ReviewInterface(algo)

        review.edit_step(1, {"description": "y = 2"})
        review.reset()

        assert review.working.steps[0].description == "x = 1"

    def test_reset_clears_pending(self):
        """Test reset clears pending edits."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1")
        ])
        review = ReviewInterface(algo)

        review.edit_step(1, {"description": "y = 2"})
        assert len(review.get_pending_changes()) == 1

        review.reset()
        assert len(review.get_pending_changes()) == 0


class TestReviewInterfaceApprove:
    """Test review interface approve."""

    def test_approve_returns_algorithm(self):
        """Test approve returns working algorithm."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1")
        ])
        review = ReviewInterface(algo)

        result = review.approve()
        assert isinstance(result, Algorithm)
        assert result.name == "test"

    def test_approve_with_changes(self):
        """Test approve returns modified algorithm."""
        algo = Algorithm(name="test", steps=[
            Step(id=1, type=StepType.ASSIGNMENT, description="x = 1")
        ])
        review = ReviewInterface(algo)

        review.edit_step(1, {"description": "y = 2"})
        result = review.approve()

        assert result.steps[0].description == "y = 2"
