"""User review interface for algorithm extraction."""

from typing import List, Dict, Any, Optional, Tuple
from copy import deepcopy

from .schema import Algorithm, Step, StepType


def validate_step_edit(step: Step, edits: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate proposed edits to a step.

    Args:
        step: Original step
        edits: Dictionary of proposed changes

    Returns:
        Tuple of (is_valid, list_of_errors)

    Per D-20 from 02-CONTEXT.md.
    """
    errors = []

    # Validate step type
    if "type" in edits:
        try:
            StepType(edits["type"])
        except ValueError:
            errors.append(f"Invalid step type: {edits['type']}")

    # Validate id is positive integer
    if "id" in edits:
        if not isinstance(edits["id"], int) or edits["id"] < 1:
            errors.append("Step ID must be a positive integer")

    # Validate description is non-empty
    if "description" in edits:
        if not edits["description"] or not str(edits["description"]).strip():
            errors.append("Step description cannot be empty")

    # Validate inputs and outputs are lists of strings
    if "inputs" in edits:
        if not isinstance(edits["inputs"], list):
            errors.append("Inputs must be a list")
        elif not all(isinstance(x, str) for x in edits["inputs"]):
            errors.append("All inputs must be strings")

    if "outputs" in edits:
        if not isinstance(edits["outputs"], list):
            errors.append("Outputs must be a list")
        elif not all(isinstance(x, str) for x in edits["outputs"]):
            errors.append("All outputs must be strings")

    return len(errors) == 0, errors


class ReviewInterface:
    """
    Interface for reviewing and editing extracted algorithms.

    Per D-18, D-19 from 02-CONTEXT.md.
    """

    def __init__(self, algorithm: Algorithm):
        self.original = algorithm
        self.working = deepcopy(algorithm)
        self.pending_edits: List[Dict] = []

    def get_side_by_side(self) -> Dict[str, Any]:
        """
        Get side-by-side view data for UI rendering.

        Returns:
            Dict with original_text and structured_steps for display

        Per D-18 from 02-CONTEXT.md.
        """
        return {
            "original_text": self.original.source_text,
            "algorithm_name": self.working.name,
            "inputs": self.working.inputs,
            "outputs": self.working.outputs,
            "steps": [
                {
                    "id": step.id,
                    "type": step.type.value,
                    "description": step.description,
                    "inputs": step.inputs,
                    "outputs": step.outputs,
                    "line_refs": step.line_refs
                }
                for step in self.working.steps
            ],
            "step_count": len(self.working.steps)
        }

    def edit_step(self, step_id: int, edits: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Edit a specific step.

        Args:
            step_id: ID of step to edit
            edits: Dictionary of changes {field: new_value}

        Returns:
            Tuple of (success, errors)

        Per D-19 from 02-CONTEXT.md.
        """
        # Find step
        step = self._find_step(step_id)
        if not step:
            return False, [f"Step {step_id} not found"]

        # Validate edits
        is_valid, errors = validate_step_edit(step, edits)
        if not is_valid:
            return False, errors

        # Apply edits
        if "type" in edits:
            step.type = StepType(edits["type"])
        if "description" in edits:
            step.description = edits["description"]
        if "inputs" in edits:
            step.inputs = edits["inputs"]
        if "outputs" in edits:
            step.outputs = edits["outputs"]
        if "expression" in edits:
            step.expression = edits["expression"]
        if "condition" in edits:
            step.condition = edits["condition"]

        self.pending_edits.append({"action": "edit", "step_id": step_id, "edits": edits})
        return True, []

    def reorder_step(self, step_id: int, new_position: int) -> Tuple[bool, str]:
        """
        Move a step to a new position.

        Args:
            step_id: ID of step to move
            new_position: New position index (1-based)

        Returns:
            Tuple of (success, message)

        Per D-19 from 02-CONTEXT.md.
        """
        steps = self.working.steps

        # Find current index
        current_idx = None
        for i, step in enumerate(steps):
            if step.id == step_id:
                current_idx = i
                break

        if current_idx is None:
            return False, f"Step {step_id} not found"

        # Clamp position
        new_position = max(1, min(new_position, len(steps)))
        new_idx = new_position - 1

        if current_idx == new_idx:
            return True, "No change needed"

        # Move step
        step = steps.pop(current_idx)
        steps.insert(new_idx, step)

        # Renumber all steps
        self._renumber_steps()

        self.pending_edits.append({"action": "reorder", "step_id": step_id, "new_position": new_position})
        return True, f"Step moved to position {new_position}"

    def delete_step(self, step_id: int) -> Tuple[bool, str]:
        """
        Delete a step.

        Args:
            step_id: ID of step to delete

        Returns:
            Tuple of (success, message)

        Per D-19 from 02-CONTEXT.md.
        """
        steps = self.working.steps

        for i, step in enumerate(steps):
            if step.id == step_id:
                steps.pop(i)
                self._renumber_steps()
                self.pending_edits.append({"action": "delete", "step_id": step_id})
                return True, f"Step {step_id} deleted"

        return False, f"Step {step_id} not found"

    def add_step(self, position: int, step_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Add a new step at specified position.

        Args:
            position: Position to insert (1-based, or -1 for end)
            step_data: Step data dictionary

        Returns:
            Tuple of (success, errors_or_message)

        Per D-19 from 02-CONTEXT.md.
        """
        # Validate
        temp_step = Step(id=0, type=StepType.COMMENT, description="")
        is_valid, errors = validate_step_edit(temp_step, step_data)
        if not is_valid:
            return False, errors

        # Create step
        step = Step(
            id=0,  # Will be renumbered
            type=StepType(step_data.get("type", "comment")),
            description=step_data.get("description", ""),
            inputs=step_data.get("inputs", []),
            outputs=step_data.get("outputs", []),
            line_refs=[]
        )

        # Insert
        steps = self.working.steps
        if position == -1 or position > len(steps):
            steps.append(step)
        else:
            steps.insert(position - 1, step)

        self._renumber_steps()

        self.pending_edits.append({"action": "add", "position": position, "step_data": step_data})
        return True, [f"Step added at position {position}"]

    def _find_step(self, step_id: int) -> Optional[Step]:
        """Find step by ID."""
        for step in self.working.steps:
            if step.id == step_id:
                return step
        return None

    def _renumber_steps(self):
        """Renumber all steps sequentially."""
        for i, step in enumerate(self.working.steps, 1):
            step.id = i

    def get_pending_changes(self) -> List[Dict]:
        """Get list of pending edits."""
        return self.pending_edits

    def reset(self):
        """Reset to original algorithm."""
        self.working = deepcopy(self.original)
        self.pending_edits = []

    def approve(self) -> Algorithm:
        """
        Approve and return final algorithm.

        Per D-22 from 02-CONTEXT.md.
        """
        return self.working


def apply_edits(algorithm: Algorithm, edits: List[Dict]) -> Algorithm:
    """
    Apply a series of edits to an algorithm.

    Args:
        algorithm: Original algorithm
        edits: List of edit operations

    Returns:
        Modified algorithm
    """
    review = ReviewInterface(algorithm)

    for edit in edits:
        action = edit.get("action")

        if action == "edit":
            review.edit_step(edit["step_id"], edit["edits"])
        elif action == "reorder":
            review.reorder_step(edit["step_id"], edit["new_position"])
        elif action == "delete":
            review.delete_step(edit["step_id"])
        elif action == "add":
            review.add_step(edit["position"], edit["step_data"])

    return review.approve()
