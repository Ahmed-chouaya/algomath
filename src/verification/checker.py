"""Execution verification checker for AlgoMath.

Per VER-01: Verify execution completed without errors.
Implements decisions D-05 from 05-CONTEXT.md.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class VerificationStatus(Enum):
    """Verification status enumeration.

    SUCCESS: All checks passed, execution was successful
    FAILED: Execution failed (timeout, error, etc.)
    ERROR: Verification itself encountered an error
    INCOMPLETE: Verification could not be completed
    """
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"
    INCOMPLETE = "incomplete"


@dataclass
class VerificationResult:
    """Result of execution verification.

    Per D-05: Provides brief summary (1-2 sentences) of execution.

    Attributes:
        status: Overall verification status
        message: Human-readable verification message
        checks_performed: List of verification checks that were run
        execution_summary: 1-2 sentence summary per D-05
        runtime_seconds: Execution runtime in seconds
        output_size: Size of output in characters
        timestamp: ISO timestamp when verification was performed
    """
    status: VerificationStatus
    message: str
    checks_performed: List[str] = field(default_factory=list)
    execution_summary: str = ""
    runtime_seconds: float = 0.0
    output_size: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for JSON serialization."""
        return {
            'status': self.status.value,
            'message': self.message,
            'checks_performed': self.checks_performed,
            'execution_summary': self.execution_summary,
            'runtime_seconds': self.runtime_seconds,
            'output_size': self.output_size,
            'timestamp': self.timestamp
        }

    def to_json(self) -> str:
        """Serialize result to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class ExecutionChecker:
    """Checker that verifies execution results.

    Performs various checks on execution output to verify:
    - No errors occurred during execution
    - Output is present (non-empty)
    - Execution completed within expected parameters
    """

    def __init__(self, results: Dict[str, Any]):
        """Initialize checker with execution results.

        Args:
            results: Dictionary containing execution results with keys:
                - status: 'success', 'timeout', 'error', etc.
                - stdout: Captured standard output
                - stderr: Captured standard error
                - runtime_seconds: Execution time
                - return_value: Optional return value
                - error_type: Optional error type
                - error_message: Optional error message
        """
        self.results = results
        self._checks_performed: List[str] = []

    def check(self) -> VerificationResult:
        """Run all verification checks.

        Returns:
            VerificationResult with status and summary
        """
        self._checks_performed = []

        # Check for errors
        no_errors, error_msg = self._check_no_errors()
        self._checks_performed.append("no_errors")

        # Check output presence
        output_present, output_msg = self._check_output_present()
        self._checks_performed.append("output_present")

        # Determine overall status
        if not no_errors:
            status = VerificationStatus.ERROR
            if self.results.get('status') == 'timeout':
                status = VerificationStatus.FAILED
            message = error_msg
        elif not output_present:
            status = VerificationStatus.FAILED
            message = output_msg
        else:
            status = VerificationStatus.SUCCESS
            message = "Execution completed successfully with no errors detected."

        # Generate summary per D-05
        summary = self._generate_summary()

        # Calculate output size
        stdout = self.results.get('stdout', '')
        stderr = self.results.get('stderr', '')
        output_size = len(stdout) + len(stderr)

        return VerificationResult(
            status=status,
            message=message,
            checks_performed=self._checks_performed.copy(),
            execution_summary=summary,
            runtime_seconds=self.results.get('runtime_seconds', 0.0),
            output_size=output_size
        )

    def _check_no_errors(self) -> Tuple[bool, str]:
        """Check if execution completed without errors.

        Returns:
            Tuple of (passed, message)
        """
        status = self.results.get('status', 'unknown')

        if status == 'success':
            return True, "No errors detected."
        elif status == 'timeout':
            return False, "Execution timed out."
        elif status in ('error', 'runtime_error', 'syntax_error', 'memory_error', 'import_error'):
            return False, f"Execution failed with status: {status}"
        else:
            return False, f"Unknown execution status: {status}"

    def _check_output_present(self) -> Tuple[bool, str]:
        """Check if output is present (non-empty).

        Returns:
            Tuple of (passed, message)
        """
        stdout = self.results.get('stdout', '')

        if stdout and len(stdout.strip()) > 0:
            return True, "Output is present."
        else:
            return False, "No output produced."

    def _generate_summary(self) -> str:
        """Generate 1-2 sentence summary per D-05.

        For success: "Algorithm completed successfully, producing [X] lines
        of output in [Y] seconds."

        For failure: "Execution encountered a [error type] after [Y] seconds."

        Returns:
            Brief summary string
        """
        status = self.results.get('status', 'unknown')
        runtime = self.results.get('runtime_seconds', 0.0)
        stdout = self.results.get('stdout', '')

        if status == 'success':
            line_count = stdout.count('\n') + (1 if stdout and not stdout.endswith('\n') else 0)
            if line_count == 0 and stdout:
                line_count = 1
            return f"Algorithm completed successfully, producing {line_count} lines of output in {runtime:.2f} seconds."
        elif status == 'timeout':
            return f"Execution encountered a timeout after {runtime:.2f} seconds."
        elif status in ('error', 'runtime_error'):
            error_type = self.results.get('error_type', 'error')
            return f"Execution encountered a {error_type} after {runtime:.2f} seconds."
        elif status == 'syntax_error':
            return f"Execution encountered a syntax error after {runtime:.2f} seconds."
        elif status == 'memory_error':
            return f"Execution encountered a memory error after {runtime:.2f} seconds."
        else:
            return f"Execution completed with status '{status}' after {runtime:.2f} seconds."


def verify_execution(results: Dict[str, Any]) -> VerificationResult:
    """High-level interface to verify execution results.

    Args:
        results: Dictionary containing execution results

    Returns:
        VerificationResult with verification status and summary
    """
    checker = ExecutionChecker(results)
    return checker.check()


__all__ = [
    'VerificationStatus',
    'VerificationResult',
    'ExecutionChecker',
    'verify_execution',
]
