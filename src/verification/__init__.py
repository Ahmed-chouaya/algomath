"""Verification module for AlgoMath.

Provides execution verification and expected results comparison.

This module implements VER-01 (verify execution without errors) and
VER-02 (compare output against expected results) requirements.

Example:
    >>> from src.verification import verify_execution, compare_outputs
    >>> 
    >>> # Verify execution results
    >>> results = {'status': 'success', 'stdout': 'output', 'runtime_seconds': 1.5}
    >>> verification = verify_execution(results)
    >>> print(verification.execution_summary)
    
    >>> # Compare expected vs actual
    >>> comparison = compare_outputs(expected='42', actual='42')
    >>> print(comparison.format_inline())
"""

from .checker import (
    ExecutionChecker,
    VerificationResult,
    VerificationStatus,
    verify_execution,
)

from .comparison import (
    ComparisonResult,
    ComparisonStatus,
    OutputComparator,
    compare_outputs,
    prompt_for_expected,
)

__all__ = [
    # Checker exports
    'ExecutionChecker',
    'VerificationResult',
    'VerificationStatus',
    'verify_execution',
    # Comparison exports
    'ComparisonResult',
    'ComparisonStatus',
    'OutputComparator',
    'compare_outputs',
    'prompt_for_expected',
]

# Version information
__version__ = "1.0.0"


def get_version() -> str:
    """Return the version of the verification module."""
    return __version__


def get_available_checks() -> list:
    """Return list of available verification checks.
    
    Returns:
        List of check names that can be performed
    """
    return [
        'no_errors',
        'output_present',
        'expected_comparison',
    ]
