"""Output formatting and display for execution results.

Covers EXE-05 (status reporting) and output formatting per D-13 through D-16.
Reuses progress indicator pattern from Phase 1 (D-09).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any

from .errors import ErrorDetails, ExecutionError


# Constants per D-15
MAX_INLINE_LINES = 50
TRUNCATION_MESSAGE = "\n... ({} more lines - see full log for details)\n"


@dataclass
class FormattedResult:
    """Formatted execution result per D-14, D-16.

    Attributes:
        display_text: Formatted text for display
        status_emoji: Visual status indicator
        status_text: Text status (Success/Failed/Timed Out)
        execution_time: Human-readable execution time
        output_truncated: Whether output was truncated
        full_log_path: Path to full log file (if exists)
    """
    display_text: str
    status_emoji: str
    status_text: str
    execution_time: str
    output_truncated: bool
    full_log_path: Optional[str]


class ExecutionFormatter:
    """Format execution results for display per D-14, D-15, D-16.

    Takes raw execution results and formats them for user presentation
    with status indicators, truncated output, and log references.
    """

    def __init__(self, algorithm_name: Optional[str] = None):
        """Initialize formatter with optional algorithm name.

        Args:
            algorithm_name: Name of the algorithm (for log path)
        """
        self.algorithm_name = algorithm_name
        self.log_dir = Path(".algomath/algorithms") / algorithm_name if algorithm_name else None

    def format_results(self, result: Any) -> FormattedResult:
        """Format execution result for display per D-14, D-15, D-16.

        Args:
            result: Execution result object with status, stdout, stderr, runtime_seconds

        Returns:
            FormattedResult with display-ready text
        """
        # Status indicators per EXE-05
        if result.status == 'success':
            emoji = '✓'
            status = 'Success'
        elif result.status == 'timeout':
            emoji = '⏱'
            status = 'Timed Out'
        else:
            emoji = '✗'
            status = 'Failed'

        # Build display text
        lines = []
        lines.append(f"{emoji} Execution: {status}")

        # Execution time per D-16
        runtime = getattr(result, 'runtime_seconds', 0)
        lines.append(f"Time: {runtime:.3f}s")

        # Output per D-13 (dual capture) and D-15 (truncation)
        stdout = getattr(result, 'stdout', '') or ''
        stderr = getattr(result, 'stderr', '') or ''

        if stdout:
            lines.append("\n--- Output ---")
            output = truncate_output(stdout, MAX_INLINE_LINES)
            lines.append(output)

        # Errors (fewer lines shown)
        if stderr:
            lines.append("\n--- Errors ---")
            errors = truncate_output(stderr, 20)  # Fewer error lines
            lines.append(errors)

        # Full log path per D-14
        log_path = str(self.log_dir / "execution.log") if self.log_dir else None
        output_truncated = len(stdout.split('\n')) > MAX_INLINE_LINES if stdout else False

        if log_path and output_truncated:
            lines.append(f"\nFull log: {log_path}")

        return FormattedResult(
            display_text='\n'.join(lines),
            status_emoji=emoji,
            status_text=status,
            execution_time=f"{runtime:.3f}s",
            output_truncated=output_truncated,
            full_log_path=log_path
        )


def truncate_output(text: str, max_lines: int = MAX_INLINE_LINES) -> str:
    """Truncate output to max_lines with summary per D-15.

    Args:
        text: Output text to truncate
        max_lines: Maximum number of lines to show

    Returns:
        Truncated text with summary message if needed
    """
    if not text:
        return text

    lines = text.split('\n')
    if len(lines) <= max_lines:
        return text

    truncated = '\n'.join(lines[:max_lines])
    remaining = len(lines) - max_lines
    return truncated + TRUNCATION_MESSAGE.format(remaining)


def show_progress(phase: str, current: int, total: int) -> str:
    """Generate progress bar string per Phase 1 D-09.

    Args:
        phase: Name of the current phase
        current: Current step number
        total: Total number of steps

    Returns:
        Formatted progress bar string like "Execute: █████░░░░░ 50%"
    """
    if total <= 0:
        return f"{phase}: ░░░░░░░░░░ 0%"

    filled = int(10 * current / total)
    filled = max(0, min(filled, 10))  # Clamp to 0-10 range
    bar = '█' * filled + '░' * (10 - filled)
    pct = int(100 * current / total)
    return f"{phase}: {bar} {pct}%"


def show_execution_summary(
    result: Any,
    error_details: Optional[ErrorDetails] = None
) -> str:
    """Show execution summary with error translation if needed per EXE-05, EXE-06.

    Args:
        result: Execution result object
        error_details: Optional error translation details

    Returns:
        Formatted summary string
    """
    lines = []

    # Status line per EXE-05
    runtime = getattr(result, 'runtime_seconds', 0)
    if result.status == 'success':
        lines.append(f"✓ Algorithm executed successfully in {runtime:.3f}s")
    else:
        lines.append(f"✗ Execution {result.status}")

    # Error translation per EXE-06
    if error_details:
        lines.append(f"\n{error_details.user_message}")
        lines.append(f"\n💡 {error_details.hint}")

        # Technical details in collapsed section per D-19
        if error_details.technical_details:
            lines.append(f"\n<details>")
            lines.append(f"<summary>Technical Details (for debugging)</summary>")
            lines.append(f"\n```\n{error_details.technical_details}\n```")
            lines.append(f"</details>")

    return '\n'.join(lines)


def format_execution_log(
    algorithm_name: str,
    status: str,
    runtime_seconds: float,
    stdout: str,
    stderr: str,
    error_type: Optional[str] = None,
    error_message: Optional[str] = None
) -> str:
    """Format complete execution log for file persistence per D-14.

    Args:
        algorithm_name: Name of the algorithm
        status: Execution status
        runtime_seconds: Execution time in seconds
        stdout: Standard output
        stderr: Standard error
        error_type: Type of error if failed
        error_message: Error message if failed

    Returns:
        Formatted log content for saving to file
    """
    from datetime import datetime

    lines = [
        f"Algorithm: {algorithm_name}",
        f"Status: {status}",
        f"Timestamp: {datetime.now().isoformat()}",
        f"Runtime: {runtime_seconds:.3f}s",
        "",
        "=" * 50,
        "OUTPUT",
        "=" * 50,
        stdout if stdout else "(no output)",
    ]

    if stderr:
        lines.extend([
            "",
            "=" * 50,
            "ERRORS",
            "=" * 50,
            stderr
        ])

    if error_type:
        lines.extend([
            "",
            "=" * 50,
            "ERROR DETAILS",
            "=" * 50,
            f"Type: {error_type}",
            f"Message: {error_message or '(no message)'}"
        ])

    return '\n'.join(lines)


__all__ = [
    'ExecutionFormatter',
    'FormattedResult',
    'truncate_output',
    'show_progress',
    'show_execution_summary',
    'format_execution_log',
]
