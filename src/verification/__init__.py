"""Verification module for AlgoMath.

Provides execution verification, comparison, explanation, and edge case detection.
"""

# From checker.py (existing)
from .checker import (
    ExecutionChecker,
    VerificationResult,
    VerificationStatus,
    verify_execution,
)

# From comparison.py (existing)
from .comparison import (
    ComparisonResult,
    ComparisonStatus,
    OutputComparator,
    compare_outputs,
    prompt_for_expected,
)

# From explainer.py (new)
from .explainer import (
    AlgorithmExplainer,
    ExplanationResult,
    ExplanationLevel,
    StepExplanation,
    explain_algorithm,
)

# From static_analysis.py (new)
from .static_analysis import (
    EdgeCaseDetector,
    EdgeCase,
    EdgeCaseSeverity,
    detect_edge_cases,
)

__all__ = [
    # Checker
    'ExecutionChecker',
    'VerificationResult',
    'VerificationStatus',
    'verify_execution',
    # Comparison
    'ComparisonResult',
    'ComparisonStatus',
    'OutputComparator',
    'compare_outputs',
    'prompt_for_expected',
    # Explainer
    'AlgorithmExplainer',
    'ExplanationResult',
    'ExplanationLevel',
    'StepExplanation',
    'explain_algorithm',
    # Edge Case Detection
    'EdgeCaseDetector',
    'EdgeCase',
    'EdgeCaseSeverity',
    'detect_edge_cases',
]
