"""Execution module for AlgoMath.

Provides safe, sandboxed code execution with resource limits,
timeout protection, and comprehensive output capture.

Per Phase 4 decisions D-01 through D-30:
- D-01: Subprocess-based isolation
- D-02: Resource limits (CPU, memory)
- D-05: 30-second default timeout
- D-09, D-10: Temp directory sandbox with auto-cleanup
- D-16: Execution metadata capture
- D-17: Error categorization
- D-28: Import restrictions
- D-29: Input handling
- D-30: Return value capture

Example:
    >>> from src.execution import execute_code, ExecutionConfig
    >>> config = ExecutionConfig(timeout=60, max_memory_mb=1024)
    >>> result = execute_code('print("Hello")', config=config)
    >>> print(result.stdout)
    "Hello"
    >>> print(result.status)
    "success"
"""

# Core sandbox and executor components
from .sandbox import SandboxExecutor, ExecutionResult, ExecutionStatus, execute_sandboxed
from .executor import execute_code, ExecutionConfig, format_results_for_context, build_execution_response

# Error handling and display (from existing modules)
from .errors import (
    ExecutionError,
    ErrorTranslator,
    ErrorDetails,
    categorize_error,
    extract_line_number,
)
from .display import (
    ExecutionFormatter,
    FormattedResult,
    truncate_output,
    show_progress,
    show_execution_summary,
    format_execution_log,
)

__version__ = "0.1.0"

__all__ = [
    # Sandbox components
    'SandboxExecutor',
    'ExecutionResult',
    'ExecutionStatus',
    'execute_sandboxed',
    # High-level interface
    'execute_code',
    'ExecutionConfig',
    'format_results_for_context',
    'build_execution_response',
    # Error handling
    'ExecutionError',
    'ErrorTranslator',
    'ErrorDetails',
    'categorize_error',
    'extract_line_number',
    # Display formatting
    'ExecutionFormatter',
    'FormattedResult',
    'truncate_output',
    'show_progress',
    'show_execution_summary',
    'format_execution_log',
]
