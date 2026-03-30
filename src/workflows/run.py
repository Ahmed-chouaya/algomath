"""
Execution workflow for AlgoMath.

This module implements the code execution phase, running
generated code in a controlled environment.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.execution import execute_code, ExecutionConfig, ExecutionStatus


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


def run_execution(
    context,
    inputs: Optional[Dict[str, Any]] = None,
    skip_execution: bool = False
) -> Dict[str, Any]:
    """
    Execute generated code.

    Per D-21: Auto-triggered after code approval.
    Per D-22: Transitions CODE_GENERATED → EXECUTING → EXECUTION_COMPLETE.
    Per D-23: Shows progress during execution.
    Per D-25: Can skip execution (user controls flow).

    Args:
        context: ContextManager instance
        inputs: Optional input data for the algorithm
        skip_execution: If True, skip execution and return mock results

    Returns:
        Dict with execution status and results

    Example:
        >>> ctx = ContextManager()
        >>> ctx.start_session()
        >>> ctx.save_code("def test(): pass")
        >>> result = run_execution(ctx)
        >>> print(result['status'])
        'success'
    """
    # Progress: Starting per D-23
    progress = show_progress("Execute", 2, 10)
    print(f"\n{progress}")
    print("Setting up execution environment...")

    # Check if code exists
    try:
        algorithm_data = context.store.load_session()
        code = algorithm_data.get('code', '')

        if not code:
            return {
                'status': 'needs_generation',
                'progress': progress,
                'message': 'No code found. Generate code first with /algo-generate',
                'next_steps': [
                    'Generate code with /algo-generate',
                    'Extract algorithm with /algo-extract',
                    'Check status with /algo-status'
                ]
            }
    except Exception as e:
        return {
            'status': 'error',
            'progress': progress,
            'message': f'Could not load algorithm data: {e}',
            'next_steps': [
                'Start over with /algo-extract',
                'Show help with /algo-help'
            ]
        }

    # Per D-25: Skip execution if requested
    if skip_execution:
        mock_results = {
            'status': 'skipped',
            'stdout': 'Execution skipped per user request.',
            'stderr': '',
            'execution_time': 0.0,
            'return_value': None,
            'error_type': None,
            'error_message': None,
            'timestamp': datetime.now().isoformat()
        }
        context.save_results(mock_results)
        progress = show_progress("Execute", 10, 10)
        return {
            'status': 'skipped',
            'progress': progress,
            'message': 'Execution skipped. Proceed to verification.',
            'next_steps': [
                'Verify manually with /algo-verify',
                'Run with /algo-run',
                'Regenerate with /algo-generate'
            ]
        }

    # Progress: Executing
    progress = show_progress("Execute", 5, 10)
    print(f"\n{progress}")
    print("Running algorithm (timeout: 30s)...")

    # Configure execution per D-05, D-02
    config = ExecutionConfig(
        timeout=30,
        max_memory_mb=512
    )

    # Execute code
    result = execute_code(code, inputs=inputs, config=config)

    # Progress: Saving
    progress = show_progress("Execute", 8, 10)
    print(f"\n{progress}")
    print("Capturing results...")

    # Format results for context per D-16
    results_data = {
        'status': result.status.value,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'execution_time': result.runtime_seconds,
        'return_value': result.return_value,
        'error_type': result.error_type,
        'error_message': result.error_message,
        'timestamp': datetime.now().isoformat()
    }

    # Save to context (triggers EXECUTION_COMPLETE transition per D-22)
    context.save_results(results_data)

    # Final progress per D-23
    progress = show_progress("Execute", 10, 10)

    # Build response per D-18
    if result.status == ExecutionStatus.SUCCESS:
        message = f"✓ Execution complete in {result.runtime_seconds:.3f}s"
    elif result.status == ExecutionStatus.TIMEOUT:
        message = "⚠ Execution timed out (30s limit). Check for infinite loops."
    else:
        message = f"✗ Execution failed: {result.error_message or result.error_type or 'Unknown error'}"

    return {
        'status': result.status.value,
        'progress': progress,
        'execution_time': result.runtime_seconds,
        'stdout': result.stdout[:2000] if result.stdout else '',  # per D-15
        'stderr': result.stderr[:1000] if result.stderr else '',
        'error': result.error_message if result.status != ExecutionStatus.SUCCESS else None,
        'message': message,
        'next_steps': [
            'Verify results with /algo-verify',
            'Run again with /algo-run',
            'Regenerate code with /algo-generate'
        ]
    }
