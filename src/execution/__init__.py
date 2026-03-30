"""Execution module for AlgoMath.

Provides error handling, display formatting, and output management
for algorithm execution phase.

Modules:
    errors: Error categorization and translation
    display: Output formatting and progress indicators
"""

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
