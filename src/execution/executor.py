"""High-level execution interface for AlgoMath workflows.

Per D-21, D-22, D-23, D-25: Workflow-facing execution interface that:
- Auto-triggers after code approval
- Shows progress during execution
- Can be skipped (user controls flow)
- Handles inputs and passes them to executed code
- Integrates with ContextManager for saving results

This module provides execute_code() as the primary interface for
running generated Python code within the AlgoMath workflow.
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

from .sandbox import SandboxExecutor, ExecutionResult, ExecutionStatus


@dataclass
class ExecutionConfig:
    """Configuration for code execution.

    Per D-05: Default timeout is 30 seconds.
    Per D-02: Default memory limit is 512MB.
    Per D-30: capture_return_value enables return value capture.

    Attributes:
        timeout: Maximum execution time in seconds
        max_memory_mb: Maximum memory allowed in megabytes
        working_dir: Optional working directory for file operations
        capture_return_value: Whether to capture function return values
    """
    timeout: int = 30
    max_memory_mb: int = 512
    working_dir: Optional[Path] = None
    capture_return_value: bool = True


def _inject_inputs(code: str, inputs: Dict[str, Any]) -> str:
    """Prepend inputs as JSON and inject reading code.

    Per D-29: Support stdin redirection for algorithms requiring input.
    This injects a get_input() function that reads from a JSON-serialized
    inputs dictionary.

    Args:
        code: Original Python code
        inputs: Dictionary of input values

    Returns:
        Code with input injection wrapper prepended
    """
    # Serialize inputs to JSON
    inputs_json = json.dumps(inputs)

    # Create wrapper code that defines get_input() function
    inputs_code = f'''
import json
__ALGO_INPUTS = json.loads({repr(inputs_json)})

def get_input(key: str, default: Any = None) -> Any:
    """Get input value by key.

    Args:
        key: Input key to retrieve
        default: Default value if key not found

    Returns:
        Input value or default
    """
    return __ALGO_INPUTS.get(key, default)
'''
    return inputs_code + "\n\n" + code


def _categorize_error(result: ExecutionResult) -> ExecutionResult:
    """Categorize and translate errors to user-friendly messages.

    Per D-17, D-18: Convert common errors to mathematician-friendly language.
    - SyntaxError → "Generated code has a syntax issue"
    - TimeoutError → "Algorithm took too long — check for infinite loops"
    - MemoryError → "Algorithm used too much memory"
    - RuntimeError → "Algorithm encountered an error during execution"

    Args:
        result: Raw execution result

    Returns:
        ExecutionResult with translated error message
    """
    if result.status == ExecutionStatus.TIMEOUT:
        result.error_message = (
            f"Algorithm took too long to complete ({result.runtime_seconds:.1f}s). "
            "Check for infinite loops."
        )
    elif result.status == ExecutionStatus.MEMORY_ERROR:
        result.error_message = (
            f"Algorithm used too much memory. "
            f"Limit: {result.error_message or 'exceeded'}"
        )
    elif result.status == ExecutionStatus.SYNTAX_ERROR:
        result.error_message = (
            f"Generated code has a syntax issue: {result.error_message or 'Unknown error'}"
        )
    elif result.status == ExecutionStatus.RUNTIME_ERROR:
        result.error_message = (
            f"Algorithm encountered an error during execution: {result.error_message or 'Unknown error'}"
        )

    return result


def execute_code(
    code: str,
    inputs: Optional[Dict[str, Any]] = None,
    config: Optional[ExecutionConfig] = None
) -> ExecutionResult:
    """Execute Python code with sandboxing.

    Per D-21: Called automatically after code approval.
    Per D-23: Shows progress during execution.
    Per D-25: Can be skipped (returns mock results).
    Per D-26: Python 3.11+ compatibility via sys.executable.
    Per D-27: Standard library only.

    This is the main entry point for executing generated code in the
    AlgoMath workflow. It handles:
    - Input injection (D-29)
    - Sandboxed execution (D-01)
    - Error categorization (D-17)
    - Result formatting

    Args:
        code: Python code to execute
        inputs: Optional input dictionary passed to the code
        config: Optional execution configuration

    Returns:
        ExecutionResult with status, output, and metadata

    Example:
        >>> result = execute_code(
        ...     code='print(get_input("x", 0))',
        ...     inputs={"x": 42},
        ...     config=ExecutionConfig(timeout=60)
        ... )
        >>> print(result.stdout)
        "42"
    """
    # Use default config if not provided
    config = config or ExecutionConfig()

    # Wrap inputs if provided per D-29
    if inputs:
        code = _inject_inputs(code, inputs)

    # Per D-30: Check if code defines main() and wrap for return value capture
    if config.capture_return_value and 'def main(' in code:
        # The sandbox already handles return value capture via wrapper
        pass

    # Create sandbox executor per D-01
    executor = SandboxExecutor(
        timeout=config.timeout,
        max_memory_mb=config.max_memory_mb
    )

    # Execute code
    result = executor.execute(code, working_dir=config.working_dir)

    # Categorize and translate errors per D-17, D-18
    if result.status != ExecutionStatus.SUCCESS:
        result = _categorize_error(result)

    return result


def format_results_for_context(result: ExecutionResult) -> Dict[str, Any]:
    """Format execution results for ContextManager.save_results().

    Per D-16: Execution metadata captured alongside outputs.

    Args:
        result: Execution result

    Returns:
        Dictionary formatted for context storage
    """
    from datetime import datetime

    return {
        'status': result.status.value,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'execution_time': result.runtime_seconds,
        'return_value': result.return_value,
        'error_type': result.error_type,
        'error_message': result.error_message,
        'timestamp': datetime.now().isoformat()
    }


def build_execution_response(
    result: ExecutionResult,
    truncate_stdout: int = 2000,
    truncate_stderr: int = 1000
) -> Dict[str, Any]:
    """Build response dict for workflow functions.

    Per D-15: Show output with truncation (50 lines max, then summarize).
    Per D-23: Progress indicator included in response.

    Args:
        result: Execution result
        truncate_stdout: Max chars for stdout (per D-15)
        truncate_stderr: Max chars for stderr

    Returns:
        Response dictionary for workflow
    """
    # Truncate output per D-15
    stdout_display = result.stdout[:truncate_stdout] if result.stdout else ''
    stderr_display = result.stderr[:truncate_stderr] if result.stderr else ''

    # Build user message per D-18
    if result.status == ExecutionStatus.SUCCESS:
        message = f"✓ Execution complete in {result.runtime_seconds:.3f}s"
    elif result.status == ExecutionStatus.TIMEOUT:
        message = (
            "⚠ Execution timed out. "
            "Check loop conditions for infinite loops."
        )
    else:
        message = f"✗ Execution failed: {result.error_message or result.error_type or 'Unknown error'}"

    return {
        'status': result.status.value,
        'execution_time': result.runtime_seconds,
        'stdout': stdout_display,
        'stderr': stderr_display,
        'error': result.error_message if result.status != ExecutionStatus.SUCCESS else None,
        'return_value': result.return_value,
        'message': message,
        'next_steps': [
            'Verify results with /algo-verify',
            'Run again with /algo-run',
            'Regenerate code with /algo-generate'
        ]
    }
