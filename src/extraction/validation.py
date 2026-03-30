"""Validation for extracted algorithms."""
from typing import List, Set, Dict, Tuple
from dataclasses import dataclass, field

from .schema import Algorithm, Step, StepType
from .errors import ExtractionError, ParseError, IncompleteError


@dataclass
class ValidationResult:
    """Result of algorithm validation."""

    is_valid: bool
    errors: List[ExtractionError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, error: ExtractionError):
        """Add an error and mark as invalid."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        """Add a warning (does not invalidate)."""
        self.warnings.append(warning)

    def __str__(self) -> str:
        if self.is_valid and not self.warnings:
            return "Algorithm is valid"

        lines = []
        if not self.is_valid:
            lines.append(f"Validation failed with {len(self.errors)} error(s)")
        if self.warnings:
            lines.append(f"{len(self.warnings)} warning(s)")
        return "\n".join(lines)


def validate_algorithm(algorithm: Algorithm) -> ValidationResult:
    """
    Validate an algorithm for correctness.

    Args:
        algorithm: Algorithm to validate

    Returns:
        ValidationResult with errors and warnings

    Per D-20 from 02-CONTEXT.md.
    """
    result = ValidationResult(is_valid=True)

    # Check algorithm has minimum structure
    if not algorithm.name or algorithm.name == "unnamed":
        result.add_warning("Algorithm has no name")

    if not algorithm.steps:
        result.add_error(IncompleteError(
            message="Algorithm has no steps",
            suggestion="Add at least one algorithm step"
        ))

    # Check for unique step IDs
    step_ids = [step.id for step in algorithm.steps]
    if len(step_ids) != len(set(step_ids)):
        duplicates = set([x for x in step_ids if step_ids.count(x) > 1])
        result.add_error(ParseError(
            message=f"Duplicate step IDs found: {duplicates}",
            suggestion="Ensure each step has a unique identifier"
        ))

    # Check step connectivity
    connectivity = check_step_connectivity(algorithm)
    if not connectivity.is_valid:
        result.errors.extend(connectivity.errors)
        result.is_valid = False

    # Check variable flow
    var_flow = check_variable_flow(algorithm)
    if not var_flow.is_valid:
        result.errors.extend(var_flow.errors)
        result.is_valid = False

    # Check each step individually
    for step in algorithm.steps:
        _validate_step(step, result)

    return result


def check_step_connectivity(algorithm: Algorithm) -> ValidationResult:
    """
    Check that all step references are valid.

    Validates that body/else_body references point to existing steps.

    Args:
        algorithm: Algorithm to check

    Returns:
        ValidationResult
    """
    result = ValidationResult(is_valid=True)
    step_ids = {step.id for step in algorithm.steps}

    for step in algorithm.steps:
        # Check body references
        for ref_id in step.body:
            if ref_id not in step_ids:
                result.add_error(ParseError(
                    message=f"Step {step.id} references non-existent step {ref_id} in body",
                    line_number=step.line_refs[0] if step.line_refs else None,
                    suggestion="Update reference to point to an existing step"
                ))

        # Check else_body references
        for ref_id in step.else_body:
            if ref_id not in step_ids:
                result.add_error(ParseError(
                    message=f"Step {step.id} references non-existent step {ref_id} in else_body",
                    line_number=step.line_refs[0] if step.line_refs else None,
                    suggestion="Update reference to point to an existing step"
                ))

    return result


def check_variable_flow(algorithm: Algorithm) -> ValidationResult:
    """
    Check that variables are defined before use.

    Args:
        algorithm: Algorithm to check

    Returns:
        ValidationResult
    """
    result = ValidationResult(is_valid=True)
    defined_vars: Set[str] = set()

    # Add input variables as initially defined
    for inp in algorithm.inputs:
        var_name = inp.get("name", "")
        if var_name:
            defined_vars.add(var_name.split('[')[0])  # Handle array notation

    # Track defined variables through steps
    for step in algorithm.steps:
        # Check inputs are defined
        for var in step.inputs:
            base_var = var.split('[')[0]  # Handle array indexing
            if base_var not in defined_vars and not _is_builtin_or_constant(base_var):
                result.add_warning(
                    f"Step {step.id}: Variable '{var}' may not be defined before use"
                )

        # Add outputs to defined set
        for var in step.outputs:
            base_var = var.split('[')[0]
            defined_vars.add(base_var)

    return result


def _is_builtin_or_constant(var: str) -> bool:
    """Check if variable is a builtin or constant."""
    builtins = {'True', 'False', 'None', 'len', 'range', 'sum', 'min', 'max'}
    constants = {'n', 'm', 'i', 'j', 'k', 'x', 'y', 'z'}
    return var in builtins or var in constants or var.isdigit()


def _validate_step(step: Step, result: ValidationResult):
    """Validate a single step."""

    # Check step has description
    if not step.description or not step.description.strip():
        result.add_error(IncompleteError(
            message=f"Step {step.id} has no description",
            line_number=step.line_refs[0] if step.line_refs else None
        ))

    # Type-specific validation
    if step.type == StepType.ASSIGNMENT:
        if not step.expression and '=' not in step.description:
            result.add_warning(f"Step {step.id}: Assignment without clear expression")

    elif step.type in (StepType.LOOP_FOR, StepType.LOOP_WHILE):
        if step.type == StepType.LOOP_FOR and not step.iter_var:
            result.add_warning(f"Step {step.id}: For loop without iteration variable")
        if not step.body:
            result.add_warning(f"Step {step.id}: Loop has empty body")

    elif step.type == StepType.CONDITIONAL:
        if not step.condition and 'if' in step.description.lower():
            result.add_warning(f"Step {step.id}: Conditional without explicit condition")

    elif step.type == StepType.RETURN:
        if not step.expression:
            result.add_warning(f"Step {step.id}: Return without value")

    # Check line references exist
    if not step.line_refs:
        result.add_warning(f"Step {step.id}: No line references (traceability reduced)")
