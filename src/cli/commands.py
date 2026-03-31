"""
CLI Commands for AlgoMath - User-facing command implementations.

This module provides command functions that can be called directly
or through the intent routing system. Commands follow a consistent
return format with status, progress, message, and next_steps.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from algomath.context import ContextManager
from algomath.state import WorkflowState
from src.workflows.run import run_execution


def extract_command(text: str, name: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract algorithm from mathematical text.

    Args:
        text: Mathematical text describing an algorithm
        name: Optional name for the algorithm

    Returns:
        Dict with extraction status and results
    """
    from src.workflows.extract import extract_algorithm

    ctx = ContextManager()
    ctx.start_session()

    if name:
        ctx.create_algorithm(name)

    result = extract_algorithm(ctx, text)
    return result


def generate_command() -> Dict[str, Any]:
    """
    Generate code from extracted algorithm steps.

    Returns:
        Dict with generation status and results
    """
    from src.workflows.generate import generate_code

    ctx = ContextManager()
    ctx.start_session()

    result = generate_code(ctx)
    return result


def run_command(
    skip: bool = False,
    inputs: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute generated code with /algo-run.

    Per D-21: Auto-triggered after code approval
    Per D-25: Can skip with skip=True to proceed directly to verification

    Args:
        skip: If True, skip execution and proceed to verification
        inputs: Optional input data for the algorithm

    Returns:
        Dict with execution status and results
    """
    ctx = ContextManager()
    ctx.start_session()

    current = ctx.get_current()

    # Check current state
    if current.current_state == WorkflowState.EXECUTION_COMPLETE:
        # Already executed - show results
        results = current.data.get('results', {})
        return {
            'status': 'already_executed',
            'message': 'Algorithm already executed. Run again to re-execute.',
            'results': results,
            'next_steps': [
                'Verify results with /algo-verify',
                'Re-run with /algo-run',
                'Regenerate with /algo-generate'
            ]
        }

    if current.current_state != WorkflowState.CODE_GENERATED:
        return {
            'status': 'invalid_state',
            'message': f"Cannot execute: current state is {current.current_state.value}",
            'required_state': 'code_generated',
            'next_steps': [
                'Generate code first with /algo-generate',
                'Check status with /algo-status'
            ]
        }

    # Check if skip requested per D-25
    if skip:
        # Skip execution, proceed to verification
        ctx.save_results({
            'status': 'skipped',
            'message': 'Execution skipped by user',
            'timestamp': datetime.now().isoformat()
        })

        return {
            'status': 'skipped',
            'message': 'Execution skipped. Proceeding to verification.',
            'next_steps': [
                'Verify with /algo-verify',
                'Run later with /algo-run'
            ]
        }

    # Execute
    print(f"Executing algorithm: {current.current_algorithm or '(unnamed)'}...")
    result = run_execution(ctx, inputs=inputs)

    return result


def verify_command(
    expected: Optional[Any] = None,
    step: Optional[int] = None,
    detailed: bool = False,
    diagnostic: bool = False
) -> Dict[str, Any]:
    """
    Verify execution results with /algo-verify.

    Per D-01: Quick inline summary shown automatically
    Per D-02: Full verification via this command
    Per D-03: Diagnostic mode for failed executions
    Per D-06: Detailed explanation with --detailed
    Per D-09: Interactive expected results prompt
    Per D-22: Diagnostic mode with --diagnostic

    Args:
        expected: Optional expected output for comparison
        step: Optional step ID for detailed explanation (VER-05)
        detailed: If True, generate detailed step-by-step explanation
        diagnostic: If True, run diagnostic mode for failed executions

    Returns:
        Dict with verification status and results
    """
    from src.workflows.verify import run_verification, verify_step

    ctx = ContextManager()
    ctx.start_session()

    current = ctx.get_current()

    # Check current state per D-02, D-25
    if current.current_state == WorkflowState.VERIFIED:
        # Already verified - show cached report
        algorithm_data = ctx.store.load_session()
        return {
            'status': 'already_verified',
            'message': 'Algorithm already verified. Run again for fresh verification.',
            'last_verification': algorithm_data.get('verification', {}),
            'next_steps': [
                'Re-verify with /algo-verify',
                'Extract new with /algo-extract',
                'Check status with /algo-status'
            ]
        }

    if current.current_state not in [WorkflowState.EXECUTION_COMPLETE, WorkflowState.CODE_GENERATED]:
        return {
            'status': 'not_ready',
            'message': f"Cannot verify: current state is {current.current_state.value}",
            'required_state': 'execution_complete',
            'next_steps': [
                'Run code first with /algo-run',
                'Check status with /algo-status'
            ]
        }

    # Handle step-specific explanation per VER-05
    if step is not None:
        result = verify_step(ctx, step)
        return result

    # Interactive prompt for expected results per D-09
    if expected is None and not diagnostic:
        # Note: In actual CLI, this would prompt user
        # For now, proceed without comparison
        pass

    # Run full verification per D-02
    print(f"Verifying algorithm: {current.current_algorithm or '(unnamed)'}...")
    result = run_verification(
        ctx,
        expected=expected,
        detailed=detailed,
        diagnostic=diagnostic
    )

    return result


def status_command() -> Dict[str, Any]:
    """
    Show current algorithm status and progress.

    Returns:
        Dict with current state information
    """
    ctx = ContextManager()
    ctx.start_session()

    current = ctx.get_current()
    progress = ctx.get_progress()
    progress_bar = ctx.get_progress_bar()

    return {
        'status': 'success',
        'algorithm': progress['algorithm_name'],
        'state': current.current_state.value,
        'progress_bar': progress_bar,
        'steps_completed': progress['steps_completed'],
        'steps_total': progress['steps_total'],
        'data_status': progress['data_status'],
        'has_text': 'text' in current.data,
        'has_steps': 'steps' in current.data,
        'has_code': 'code' in current.data,
        'has_results': 'results' in current.data,
        'next_steps': [
            f"Current: {current.current_state.value}",
            "Continue with workflow commands",
            "Use /algo-help for command list"
        ]
    }


def list_command() -> Dict[str, Any]:
    """
    List all saved algorithms.

    Returns:
        Dict with list of algorithms
    """
    ctx = ContextManager()
    algorithms = ctx.list_algorithms()

    return {
        'status': 'success',
        'count': len(algorithms),
        'algorithms': [
            {'name': name, 'updated': updated}
            for name, updated in algorithms
        ],
        'next_steps': [
            'Load algorithm with /algo-extract [name]',
            'Start new with /algo-extract',
            'Check status with /algo-status'
        ]
    }


def help_command() -> Dict[str, Any]:
    """
    Show help and available commands.

    Returns:
        Dict with command reference
    """
    commands = [
        ('/algo-extract "text" [name]', 'Extract algorithm from text', 'Initial'),
        ('/algo-generate', 'Generate code from steps', 'STEPS_STRUCTURED'),
        ('/algo-run', 'Execute generated code', 'CODE_GENERATED'),
        ('/algo-run --skip', 'Skip execution (proceed to verify)', 'CODE_GENERATED'),
        ('/algo-verify', 'Verify execution results', 'EXECUTION_COMPLETE'),
        ('/algo-verify --step N', 'Explain step N in detail', 'EXECUTION_COMPLETE'),
        ('/algo-verify --detailed', 'Show detailed explanation', 'EXECUTION_COMPLETE'),
        ('/algo-verify --diagnostic', 'Diagnose failed execution', 'EXECUTION_COMPLETE'),
        ('/algo-status', 'Show current state and progress', 'Any'),
        ('/algo-list', 'List saved algorithms', 'Any'),
        ('/algo-help', 'Show this help', 'Any'),
    ]

    return {
        'status': 'success',
        'commands': [
            {
                'command': cmd,
                'description': desc,
                'requires': req
            }
            for cmd, desc, req in commands
        ],
        'tip': 'Commands can be used naturally, e.g., "extract algorithm from this text"',
        'next_steps': [
            'Try /algo-extract to start',
            'Check /algo-status any time',
            'Ask for /algo-help when needed'
        ]
    }


# Command map for routing
COMMAND_MAP = {
    'extract': extract_command,
    'generate': generate_command,
    'run': run_command,
    'verify': verify_command,
    'status': status_command,
    'list': list_command,
    'help': help_command,
}


# Exports
__all__ = [
    'COMMAND_MAP',
    'extract_command',
    'generate_command',
    'run_command',
    'verify_command',
    'status_command',
    'list_command',
    'help_command',
]
