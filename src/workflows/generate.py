"""
Generation workflow for AlgoMath.

This module implements the code generation phase, transforming
extracted algorithm steps into executable Python code.
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
    """
    if total <= 0:
        return f"{phase}: ░░░░░░░░░░ 0%"

    filled = int(10 * current / total)
    filled = max(0, min(filled, 10))  # Clamp to 0-10 range
    bar = '█' * filled + '░' * (10 - filled)
    pct = int(100 * current / total)
    return f"{phase}: {bar} {pct}%"


def run_generation(context: "ContextManager") -> Dict[str, Any]:
    """
    Generate Python code from extracted steps using TemplateCodeGenerator.

    Args:
        context: ContextManager instance

    Returns:
        Dict with status and code generation result

    Example:
        >>> ctx = ContextManager()
        >>> ctx.start_session()
        >>> ctx.save_steps([{"step": 1, "action": "init"}])
        >>> result = run_generation(ctx)
        >>> print(result['status'])
        'code_generated'
    """
    # Import here to avoid circular imports
    from algomath.context import ContextManager
    from src.extraction.schema import Algorithm
    from src.generation import TemplateCodeGenerator

    # Progress indicator
    progress = show_progress("Generate", 1, 10)

    # Load algorithm
    try:
        algorithm_data = context.store.load_session()
        if not algorithm_data.get('algorithm'):
            return {
                'status': 'needs_extraction',
                'progress': progress,
                'message': 'No algorithm found. Extract algorithm first with /algo-extract',
                'next_steps': [
                    'Extract algorithm with /algo-extract',
                    'Check status with /algo-status'
                ]
            }
    except Exception:
        return {
            'status': 'error',
            'progress': progress,
            'message': 'Could not load algorithm data',
            'next_steps': [
                'Start over with /algo-extract',
                'Show help with /algo-help'
            ]
        }

    # Convert to Algorithm object
    try:
        algorithm = Algorithm.from_dict(algorithm_data['algorithm'])
    except Exception as e:
        return {
            'status': 'error',
            'progress': progress,
            'message': f'Failed to parse algorithm: {e}',
            'next_steps': ['Extract algorithm again with /algo-extract']
        }

    # Update progress
    progress = show_progress("Generate", 5, 10)

    # Generate code using template generator
    try:
        generator = TemplateCodeGenerator()
        generated = generator.generate(algorithm)

        # Validate syntax
        if not generated.validation_result.is_valid:
            return {
                'status': 'generation_error',
                'progress': show_progress("Generate", 7, 10),
                'error': generated.validation_result.errors,
                'message': 'Generated code has syntax errors',
                'next_steps': ['Review extraction with /algo-extract', 'Try again with /algo-generate']
            }

        # Save to context
        context.save_code(generated.source)

        # Final progress
        progress = show_progress("Generate", 10, 10)

        return {
            'status': 'code_generated',
            'progress': progress,
            'lines_of_code': len(generated.source.split('\n')),
            'algorithm_name': generated.algorithm_name,
            'message': f'Generated {generated.algorithm_name} with type hints',
            'next_steps': [
                'Review code with /algo-review',
                'Execute with /algo-run',
                'Regenerate with /algo-generate',
                'Check status with /algo-status'
            ]
        }
    except Exception as e:
        return {
            'status': 'generation_error',
            'progress': show_progress("Generate", 5, 10),
            'error': str(e),
            'message': f'Code generation failed: {e}',
            'next_steps': ['Try again with /algo-generate', 'Review extraction with /algo-extract']
        }
