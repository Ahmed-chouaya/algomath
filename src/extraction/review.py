"""Review interface for extracted algorithms."""
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from .schema import Algorithm, Step, StepType
from .errors import ExtractionError, IncompleteError


class ReviewInterface:
    """Interface for reviewing and editing extracted algorithms."""

    def __init__(self, algorithm: Algorithm):
        """Initialize with an algorithm."""
        self.original = algorithm
        self.working = deepcopy(algorithm)
        self.edits: List[Dict[str, Any]] = []

    def show_side_by_side(self) -> Dict[str, Any]:
        """Show original text and structured steps side by side."""
        return {
            "original_text": self.original.source_text,
            "structured_steps": [
                {
                    "id": step.id,
                    "type": step.type.value,
                    "description": step.description,
                    "line_refs": step.line_refs
                }
                for step in self.working.steps
            ]
        }

    def edit_step(self, step_id: int, changes: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Edit a step.
        
        Args:
            step_id: ID of step to edit
            changes: Dict of changes to apply
            
        Returns:
            (success, errors)
        """
        errors = validate_step_edit(self.working, step_id, changes)
        if errors:
            return False, errors

        # Find and update step
        for step in self.working.steps:
            if step.id == step_id:
                if "description" in changes:
                    step.description = changes["description"]
                if "type" in changes:
                    step.type = StepType(changes["type"])
                break

        self.edits.append({"action": "edit", "step_id": step_id, "changes": changes})
        return True, []

    def delete_step(self, step_id: int) -> bool:
        """Delete a step."""
        self.working.steps = [s for s in self.working.steps if s.id != step_id]
        self.edits.append({"action": "delete", "step_id": step_id})
        return True

    def add_step(self, step_data: Dict[str, Any]) -> int:
        """Add a new step."""
        new_id = max([s.id for s in self.working.steps], default=0) + 1
        step = Step(
            id=new_id,
            type=StepType(step_data.get("type", "assignment")),
            description=step_data.get("description", ""),
            line_refs=[]
        )
        self.working.steps.append(step)
        self.edits.append({"action": "add", "step_id": new_id, "data": step_data})
        return new_id

    def reorder_steps(self, new_order: List[int]) -> bool:
        """Reorder steps by new ID sequence."""
        id_map = {s.id: s for s in self.working.steps}
        self.working.steps = [id_map[i] for i in new_order if i in id_map]
        self.edits.append({"action": "reorder", "new_order": new_order})
        return True

    def approve(self) -> Algorithm:
        """Approve and return final algorithm."""
        return self.working

    def reset(self) -> None:
        """Reset to original."""
        self.working = deepcopy(self.original)
        self.edits = []


def validate_step_edit(
    algorithm: Algorithm,
    step_id: int,
    changes: Dict[str, Any]
) -> List[str]:
    """
    Validate proposed step edits.
    
    Returns list of error messages (empty if valid).
    """
    errors = []

    # Check step exists
    step = next((s for s in algorithm.steps if s.id == step_id), None)
    if step is None:
        errors.append(f"Step {step_id} not found")
        return errors

    # Validate description
    if "description" in changes:
        desc = changes["description"]
        if not desc or not desc.strip():
            errors.append("Step description cannot be empty")
        elif len(desc) > 1000:
            errors.append("Step description too long (max 1000 chars)")

    # Validate type
    if "type" in changes:
        try:
            StepType(changes["type"])
        except ValueError:
            errors.append(f"Invalid step type: {changes['type']}")

    return errors


def apply_edits(algorithm: Algorithm, edits: List[Dict[str, Any]]) -> Algorithm:
    """Apply a list of edits to an algorithm."""
    review = ReviewInterface(algorithm)
    
    for edit in edits:
        action = edit.get("action")
        if action == "edit":
            review.edit_step(edit["step_id"], edit["changes"])
        elif action == "delete":
            review.delete_step(edit["step_id"])
        elif action == "add":
            review.add_step(edit["data"])
        elif action == "reorder":
            review.reorder_steps(edit["new_order"])
    
    return review.working
