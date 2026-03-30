"""Extraction workflow for AlgoMath."""

from typing import Dict, List, Optional, Any
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import extraction components
from src.extraction.llm_extraction import HybridExtractor
from src.extraction.review import ReviewInterface
from src.extraction.schema import algorithm_to_json


def show_progress(phase: str, current: int, total: int) -> str:
    """
    Generate a progress bar string.

    Args:
        phase: Name of the current phase
        current: Current step number
        total: Total number of steps

    Returns:
        Formatted progress bar string

    Example:
    >>> show_progress("Extract", 8, 10)
    "Extract: ████████░░ 80%"
    """
    if total <= 0:
        return f"{phase}: ░░░░░░░░░░ 0%"

    filled = int(10 * current / total)
    filled = max(0, min(filled, 10))  # Clamp to 0-10 range
    bar = '█' * filled + '░' * (10 - filled)
    pct = int(100 * current / total)
    return f"{phase}: {bar} {pct}%"


def run_extraction(
    context: Any,
    text: Optional[str] = None,
    name: Optional[str] = None,
    skip_review: bool = False
) -> Dict[str, Any]:
    """
    Run the extraction workflow with hybrid extraction.

    Per EXT-01, EXT-02, EXT-03, EXT-04, EXT-05, EXT-06.
    """
    # Import here to avoid circular imports
    from algomath.context import ContextManager
    from algomath.state import WorkflowState

    # Progress: Parsing
    progress = show_progress("Extract", 1, 5)

    # Check if we have algorithm text
    if text is None:
        return {
            'status': 'needs_input',
            'progress': progress,
            'message': 'Please provide algorithm text to extract',
            'next_steps': [
                'Provide algorithm text',
                'Cancel extraction'
            ]
        }

    # Save text to context
    context.save_text(text)

    # Progress: Extracting
    progress = show_progress("Extract", 2, 5)

    # Run hybrid extraction
    extractor = HybridExtractor()
    result = extractor.extract(text, prefer_llm=True)

    if not result.success:
        return {
            'status': 'extraction_failed',
            'progress': progress,
            'errors': result.errors,
            'message': 'Failed to extract algorithm from text',
            'next_steps': [
                'Try again with clearer text',
                'Cancel extraction'
            ]
        }

    # Progress: Structuring
    progress = show_progress("Extract", 3, 5)

    # Convert steps to JSON-serializable format
    algorithm = result.algorithm
    steps_data = []
    for step in algorithm.steps:
        steps_data.append({
            'id': step.id,
            'type': step.type.value,
            'description': step.description,
            'inputs': step.inputs,
            'outputs': step.outputs,
            'line_refs': step.line_refs,
            'condition': step.condition,
            'body': step.body,
            'else_body': step.else_body,
            'iter_var': step.iter_var,
            'iter_range': step.iter_range,
            'expression': step.expression,
            'call_target': step.call_target,
            'arguments': step.arguments,
            'annotation': step.annotation
        })

    # Prepare review interface
    review = ReviewInterface(algorithm)

    # Progress: Validating
    progress = show_progress("Extract", 4, 5)

    if skip_review:
        # Auto-approve
        context.save_steps(steps_data)
    else:
        # Return for review
        context.save_steps(steps_data)  # Save tentative steps

        return {
            'status': 'needs_review',
            'progress': progress,
            'algorithm': {
                'name': algorithm.name,
                'inputs': algorithm.inputs,
                'outputs': algorithm.outputs,
                'steps': steps_data
            },
            'review_interface': review,
            'method': result.method,
            'message': 'Algorithm extracted. Please review before proceeding.',
            'next_steps': [
                'Review and approve extracted steps',
                'Edit steps if needed',
                'Regenerate with clearer text'
            ]
        }

    # Progress: Complete
    progress = show_progress("Extract", 5, 5)

    return {
        'status': 'extraction_complete',
        'progress': progress,
        'steps_extracted': len(steps_data),
        'algorithm_name': algorithm.name or (name if name else 'unnamed'),
        'method': result.method,
        'next_steps': [
            'Generate code with /algo-generate',
            'Review extracted steps: /algo-status',
            'Extract a different algorithm: /algo-extract'
        ]
    }


def get_progress_bar(step: int, total: int) -> str:
    """
    Generate progress bar string: Extract: ████████░░ 80%

    Args:
        step: Current step
        total: Total steps

    Returns:
        Progress bar string
    """
    return show_progress("Extract", step, total)
