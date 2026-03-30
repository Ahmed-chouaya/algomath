"""Error categorization and translation for execution results.

Covers EXE-05 (status reporting) and EXE-06 (meaningful error messages).
Implements decisions D-17 through D-20 from 04-CONTEXT.md.
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from subprocess import TimeoutExpired


class ExecutionError(Enum):
    """Execution error categories per D-17.

    Categorizes errors into mathematician-friendly types:
    - SYNTAX_ERROR: Code parsing issues
    - RUNTIME_ERROR: General execution failures
    - TIMEOUT_ERROR: Execution exceeded time limit
    - MEMORY_ERROR: Execution exceeded memory limit
    - SUCCESS: No error
    """
    SYNTAX_ERROR = "syntax_error"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT_ERROR = "timeout_error"
    MEMORY_ERROR = "memory_error"
    SUCCESS = "success"


@dataclass
class ErrorDetails:
    """Error details with user-friendly translation per D-19.

    Attributes:
        category: The error category (ExecutionError enum)
        user_message: Human-friendly description of what happened
        hint: Suggestion for how to fix (per D-20)
        technical_details: Full traceback/debug info for developers (optional)
        line_number: Line where error occurred (optional)
    """
    category: ExecutionError
    user_message: str
    hint: str
    technical_details: Optional[str] = None
    line_number: Optional[int] = None


class ErrorTranslator:
    """Translate technical errors to mathematician-friendly language per D-18.

    Converts Python exceptions and error messages into accessible descriptions
    that mathematicians without programming background can understand.
    """

    TRANSLATIONS = {
        ExecutionError.SYNTAX_ERROR: {
            'message': 'Generated code has a syntax issue',
            'hint': 'This is likely a translation error. Try regenerating with clearer pseudocode.'
        },
        ExecutionError.TIMEOUT_ERROR: {
            'message': 'Algorithm took too long to complete',
            'hint': 'Check for infinite loops or consider optimizing the algorithm.'
        },
        ExecutionError.MEMORY_ERROR: {
            'message': 'Algorithm used too much memory',
            'hint': 'Consider using more memory-efficient data structures or algorithms.'
        },
        ExecutionError.RUNTIME_ERROR: {
            'message': 'Algorithm encountered an error while running',
            'hint': 'Review the technical details below for debugging information.'
        },
        ExecutionError.SUCCESS: {
            'message': 'Algorithm executed successfully',
            'hint': 'No issues detected.'
        }
    }

    @classmethod
    def translate(cls, error: ExecutionError, technical: str = "") -> ErrorDetails:
        """Translate error category to user-friendly message.

        Args:
            error: The error category
            technical: Technical details for debugging (traceback, etc.)

        Returns:
            ErrorDetails with user-friendly message and hint per D-18, D-20
        """
        translation = cls.TRANSLATIONS.get(error, cls.TRANSLATIONS[ExecutionError.RUNTIME_ERROR])
        return ErrorDetails(
            category=error,
            user_message=translation['message'],
            hint=translation['hint'],
            technical_details=technical if technical else None
        )


def categorize_error(error: Exception, stderr: str = "") -> ExecutionError:
    """Categorize exception into ExecutionError type per D-17.

    Analyzes the exception type and stderr output to classify errors
    into mathematician-friendly categories.

    Args:
        error: The exception that occurred
        stderr: Standard error output from execution (optional)

    Returns:
        ExecutionError category
    """
    # Check by exception type
    if isinstance(error, TimeoutExpired):
        return ExecutionError.TIMEOUT_ERROR
    if isinstance(error, MemoryError):
        return ExecutionError.MEMORY_ERROR
    if isinstance(error, SyntaxError):
        return ExecutionError.SYNTAX_ERROR

    # Check stderr content for error indicators
    stderr_lower = stderr.lower()
    if "SyntaxError" in stderr:
        return ExecutionError.SYNTAX_ERROR
    if "MemoryError" in stderr or "out of memory" in stderr_lower:
        return ExecutionError.MEMORY_ERROR
    if "timeout" in stderr_lower or "time limit" in stderr_lower:
        return ExecutionError.TIMEOUT_ERROR

    # Default to runtime error for anything else
    return ExecutionError.RUNTIME_ERROR


def extract_line_number(traceback: str) -> Optional[int]:
    """Extract line number from Python traceback for debugging per D-19.

    Args:
        traceback: The full traceback string

    Returns:
        Line number if found, None otherwise
    """
    if not traceback:
        return None

    # Match "File "path", line N" pattern
    match = re.search(r'File "[^"]+", line (\d+)', traceback)
    if match:
        return int(match.group(1))
    return None


__all__ = [
    'ExecutionError',
    'ErrorDetails',
    'ErrorTranslator',
    'categorize_error',
    'extract_line_number',
]
