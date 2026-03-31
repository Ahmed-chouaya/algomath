"""
Verification workflow for AlgoMath.

This module implements the verification phase, checking execution
results and explaining algorithm behavior.

Implements Phase 5 verification with:
- Execution status checking (VER-01)
- Expected results comparison (VER-02)
- Algorithm behavior explanation (VER-03)
- Edge case detection (VER-04)
- Step-level explanations (VER-05)
"""

from typing import Dict, List, Optional, Any
import sys
from pathlib import Path
from datetime import datetime
import json

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.verification import (
    ExecutionChecker,
    VerificationResult,
    VerificationStatus,
    verify_execution,
    OutputComparator,
    ComparisonResult,
    ComparisonStatus,
    prompt_for_expected,
    compare_outputs,
    AlgorithmExplainer,
    ExplanationResult,
    ExplanationLevel,
    explain_algorithm,
    EdgeCaseDetector,
    EdgeCase,
    EdgeCaseSeverity,
    detect_edge_cases,
)


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


def run_verification(
    context: "ContextManager",
    expected: Optional[Any] = None,
    detailed: bool = False,
    diagnostic: bool = False
) -> Dict[str, Any]:
    """
    Run full verification workflow per VER-01 to VER-05.

    Args:
        context: ContextManager instance
        expected: Optional expected output for comparison
        detailed: If True, generate detailed explanation per D-06
        diagnostic: If True, run diagnostic mode per D-22, D-23

    Returns:
        Dict with verification status and results per D-17 format
    """
    from algomath.context import ContextManager
    from algomath.state import WorkflowState

    # Step 1: Check state and load data (progress 1-2)
    progress = show_progress("Verify", 1, 10)

    algorithm_data = context.store.load_session()
    results = algorithm_data.get('results', {})
    steps = algorithm_data.get('steps', [])
    code = algorithm_data.get('code', '')

    if not results:
        return {
            'status': 'needs_execution',
            'progress': progress,
            'message': 'No execution results found. Run code first with /algo-run',
            'next_steps': ['/algo-run', '/algo-status']
        }

    progress = show_progress("Verify", 2, 10)

    # Step 2: Verify execution status (VER-01) (progress 3)
    checker = ExecutionChecker(results)
    verification = checker.check()

    # Handle diagnostic mode per D-22, D-23
    if diagnostic and verification.status != VerificationStatus.SUCCESS:
        return _run_diagnostic(context, results, verification)

    progress = show_progress("Verify", 3, 10)

    # Step 3: Compare with expected results (VER-02) (progress 4-5)
    comparison = None
    if expected is not None:
        actual = results.get('return_value') or results.get('stdout', '').strip()
        comparison = compare_outputs(expected, actual)
        progress = show_progress("Verify", 5, 10)
    else:
        progress = show_progress("Verify", 4, 10)

    # Step 4: Explain algorithm behavior (VER-03) (progress 6-7)
    explanation = None
    if steps:
        try:
            from src.extraction.schema import Algorithm
            algorithm = Algorithm.from_dict({
                'name': algorithm_data.get('name', 'unnamed'),
                'description': algorithm_data.get('description', ''),
                'inputs': algorithm_data.get('inputs', []),
                'outputs': algorithm_data.get('outputs', []),
                'steps': steps,
                'source_text': algorithm_data.get('text', '')
            })
            level = ExplanationLevel.DETAILED if detailed else ExplanationLevel.BRIEF
            explanation = explain_algorithm(algorithm, level=level)
            progress = show_progress("Verify", 7, 10)
        except Exception as e:
            explanation = None

    if not explanation:
        progress = show_progress("Verify", 6, 10)

    # Step 5: Detect edge cases (VER-04) (progress 8)
    edge_cases = []
    if code:
        try:
            edge_cases = detect_edge_cases(code)
            progress = show_progress("Verify", 8, 10)
        except Exception:
            pass

    # Step 6: Build verification report (progress 9)
    report = _build_verification_report(
        verification=verification,
        comparison=comparison,
        explanation=explanation,
        edge_cases=edge_cases,
        results=results
    )

    progress = show_progress("Verify", 9, 10)

    # Step 7: Persist report per D-20
    _save_verification_report(context, report)

    # Step 8: Mark as verified per D-04
    context.mark_verified()

    progress = show_progress("Verify", 10, 10)

    return {
        'status': 'verified' if verification.status == VerificationStatus.SUCCESS else 'verified_with_warnings',
        'progress': progress,
        'verification_report': report,
        'message': _format_verification_message(verification, comparison),
        'next_steps': [
            'Request step explanation: /algo-verify --step 1',
            'View detailed explanation: /algo-verify --detailed',
            'Run diagnostic: /algo-verify --diagnostic' if verification.status != VerificationStatus.SUCCESS else None,
            'Extract new algorithm: /algo-extract'
        ]
    }


def verify_step(context: "ContextManager", step_id: int) -> Dict[str, Any]:
    """
    Provide detailed explanation for a specific step (VER-05).

    Args:
        context: ContextManager instance
        step_id: ID of the step to explain

    Returns:
        Dict with step explanation
    """
    from algomath.context import ContextManager

    algorithm_data = context.store.load_session()
    steps = algorithm_data.get('steps', [])

    if not steps:
        return {
            'status': 'error',
            'message': 'No algorithm steps found',
            'next_steps': ['/algo-extract', '/algo-status']
        }

    # Find step
    step_data = next((s for s in steps if s.get('id') == step_id), None)
    if not step_data:
        return {
            'status': 'error',
            'message': f'Step {step_id} not found',
            'next_steps': ['/algo-status']
        }

    # Build step explanation
    explanation = _explain_single_step(step_data, algorithm_data.get('results', {}))

    return {
        'status': 'success',
        'step_id': step_id,
        'explanation': explanation,
        'message': f'Step {step_id} explanation complete',
        'next_steps': ['Explain another step: /algo-verify --step N', 'Full verification: /algo-verify']
    }


def _run_diagnostic(context, results, verification):
    """Run diagnostic mode for failed executions per D-22, D-23."""
    error_info = results.get('error', {})
    trace = results.get('traceback', '')

    diagnostic_report = {
        'mode': 'diagnostic',
        'failure_point': error_info.get('line', 'unknown'),
        'involved_values': _extract_involved_values(trace),
        'possible_fixes': _suggest_fixes(error_info)
    }

    return {
        'status': 'diagnostic_complete',
        'diagnostic_report': diagnostic_report,
        'message': 'Diagnostic analysis complete. See report for details.',
        'next_steps': ['/algo-run', '/algo-generate', '/algo-status']
    }


def _build_verification_report(verification, comparison, explanation, edge_cases, results):
    """Build structured verification report per D-17, D-20."""
    report = {
        'summary': verification.execution_summary if verification else 'Verification unavailable',
        'execution': {
            'status': verification.status.value if verification else 'unknown',
            'runtime': getattr(verification, 'runtime_seconds', 0),
            'output_size': getattr(verification, 'output_size', 0),
            'checks_performed': verification.checks_performed if verification else []
        },
        'explanation': explanation.to_dict() if explanation else None,
        'edge_cases': [ec.to_dict() for ec in edge_cases] if edge_cases else [],
        'comparison': comparison.to_dict() if comparison else None,
        'timestamp': verification.timestamp if verification else None
    }
    return report


def _format_verification_message(verification, comparison):
    """Format user-facing message per D-05, D-11."""
    lines = [verification.execution_summary if verification else 'Verification complete']

    if comparison:
        if comparison.status == ComparisonStatus.MATCH:
            lines.append('✓ Output matches expected results')
        elif comparison.status == ComparisonStatus.MISMATCH:
            lines.append('⚠ Output differs from expected — see comparison details')

    return '\n'.join(lines)


def _explain_single_step(step_data, results):
    """Generate explanation for a single step."""
    explanation = f"Step {step_data['id']}: {step_data['description']}\n\n"

    if step_data.get('inputs'):
        explanation += f"Inputs: {', '.join(step_data['inputs'])}\n"
    if step_data.get('outputs'):
        explanation += f"Outputs: {', '.join(step_data['outputs'])}\n"

    # Add execution values if available
    execution_values = results.get('trace', {}).get(step_data['id'], {})
    if execution_values:
        explanation += f"\nExecution values: {execution_values}\n"

    return explanation


def _extract_involved_values(traceback):
    """Extract variable values from traceback per D-23."""
    return {}


def _suggest_fixes(error_info):
    """Suggest mathematical fixes per D-23."""
    suggestions = []
    error_type = error_info.get('type', '')

    if 'ZeroDivisionError' in error_type:
        suggestions.append('Check for zero values before division')
        suggestions.append('Consider adding a guard condition')
    elif 'IndexError' in error_type:
        suggestions.append('Verify array bounds are within valid range')

    return suggestions


def _save_verification_report(context, report):
    """Save verification report to file per D-20."""
    try:
        current = context.get_current()
        if current.current_algorithm:
            log_dir = Path('.algomath/algorithms') / current.current_algorithm
            log_dir.mkdir(parents=True, exist_ok=True)

            log_path = log_dir / 'verification.log'
            with open(log_path, 'w') as f:
                json.dump(report, f, indent=2)
    except Exception:
        pass  # Non-critical: log persistence failure gracefully
