"""Schema definitions for algorithm extraction.

This module defines the core data structures for representing algorithms
and their steps in a structured, machine-readable format.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class StepType(Enum):
    """Enumeration of step types for algorithm steps."""
    ASSIGNMENT = "assignment"
    LOOP_FOR = "loop_for"
    LOOP_WHILE = "loop_while"
    CONDITIONAL = "conditional"
    RETURN = "return"
    CALL = "call"
    COMMENT = "comment"


@dataclass
class Step:
    """
    Represents a single step in an algorithm.

    Attributes:
        id: Unique identifier for the step
        type: Type of step (assignment, loop, conditional, etc.)
        description: Human-readable description of the step
        inputs: List of variable names read by this step
        outputs: List of variable names written by this step
        line_refs: Line numbers in the original source text
        condition: Condition for loops/conditionals
        body: List of step IDs in the body (for loops/conditionals)
        else_body: List of step IDs in the else branch (for conditionals)
        iter_var: Loop variable (for for loops)
        iter_range: Range specification (for for loops)
        expression: Expression (for assignments and returns)
        call_target: Function name (for calls)
        arguments: Arguments (for calls)
        annotation: Comment text (for comments)
    """
    id: int
    type: StepType
    description: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    line_refs: List[int] = field(default_factory=list)
    condition: Optional[str] = None
    body: List[int] = field(default_factory=list)
    else_body: List[int] = field(default_factory=list)
    iter_var: Optional[str] = None
    iter_range: Optional[str] = None
    expression: Optional[str] = None
    call_target: Optional[str] = None
    arguments: List[str] = field(default_factory=list)
    annotation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary representation."""
        return {
            "id": self.id,
            "type": self.type.value,
            "description": self.description,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "line_refs": self.line_refs,
            "condition": self.condition,
            "body": self.body,
            "else_body": self.else_body,
            "iter_var": self.iter_var,
            "iter_range": self.iter_range,
            "expression": self.expression,
            "call_target": self.call_target,
            "arguments": self.arguments,
            "annotation": self.annotation
        }


@dataclass
class Algorithm:
    """
    Represents a complete algorithm with its steps.

    Attributes:
        name: Algorithm name
        description: Brief description
        inputs: List of input variables with types and descriptions
        outputs: List of output variables with types and descriptions
        steps: List of algorithm steps
        source_text: Original source text
    """
    name: str
    description: str = ""
    inputs: List[Dict[str, Any]] = field(default_factory=list)
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    steps: List[Step] = field(default_factory=list)
    source_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert algorithm to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "steps": [step.to_dict() for step in self.steps],
            "source_text": self.source_text
        }


def algorithm_to_json(algorithm: Algorithm) -> Dict[str, Any]:
    """
    Convert an Algorithm object to JSON-serializable dictionary.

    Args:
        algorithm: Algorithm to convert

    Returns:
        Dictionary suitable for JSON serialization
    """
    return algorithm.to_dict()
