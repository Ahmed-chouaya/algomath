"""
Extraction workflow for AlgoMath.

This module implements the algorithm extraction phase, parsing natural
language algorithm descriptions into structured step format.
"""

from typing import Dict, List, Optional, Any
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


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
    context: "ContextManager",  # Forward reference
    text: Optional[str] = None,
    name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run the extraction workflow.

    Parses algorithm text and converts it to structured steps.
    This is a stub implementation for Phase 2.

    Args:
        context: ContextManager instance for state management
        text: Optional algorithm text (if None, prompts user)
        name: Optional algorithm name for saving

    Returns:
        Dict with status and next steps

    Example:
        >>> ctx = ContextManager()
        >>> ctx.start_session()
        >>> result = run_extraction(ctx, text="Step 1: Initialize...")
        >>> print(result['status'])
        'extraction_complete'
    """
    # Progress indicator
    progress = show_progress("Extract", 1, 10)

    # Check if we have algorithm text
    if text is None:
        # In a real implementation, this would prompt the user
        # For now, return status asking for input
        return {
            'status': 'needs_input',
            'progress': progress,
            'message': 'Please provide algorithm text to extract',
            'next_steps': [
                'Provide algorithm text',
                'Cancel extraction'
            ]
        }

    # Import here to avoid circular imports
    from algomath.context import ContextManager
    from algomath.state import WorkflowState

    # Save text to context
    context.save_text(text)

    # Update progress
    progress = show_progress("Extract", 5, 10)

    # Simulate extraction (Phase 2 will implement actual parsing)
    extracted_steps = [
        {"step": 1, "action": "placeholder", "description": "Extraction to be implemented in Phase 2"}
    ]

    context.save_steps(extracted_steps)

    # Final progress
    progress = show_progress("Extract", 10, 10)

    # Return result
    return {
        'status': 'extraction_complete',
        'progress': progress,
        'steps_extracted': len(extracted_steps),
        'algorithm_name': name or 'unnamed',
        'next_steps': [
            'Generate code with /algo-generate',
            'Review extracted text with /algo-status',
            'Extract a different algorithm with /algo-extract'
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
