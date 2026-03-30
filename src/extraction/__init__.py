"""AlgoMath Extraction Module.

Provides functionality for extracting structured algorithms from
mathematical text descriptions.

Usage:
    from src.extraction import HybridExtractor, Algorithm

    extractor = HybridExtractor()
    result = extractor.extract(text)

    if result.success:
        print(f"Extracted: {result.algorithm.name}")
        for step in result.algorithm.steps:
            print(f"  {step.id}. {step.description}")
"""

# Core types
from .schema import (
    Algorithm,
    Step,
    StepType,
    algorithm_to_json,
    algorithm_from_json,
)

# Parsing
from .parser import (
    RuleBasedParser,
    parse_algorithm,
)

# LLM Extraction
from .llm_extraction import (
    HybridExtractor,
    extract_algorithm_llm,
    ExtractionResult,
)

# Review
from .review import (
    ReviewInterface,
    validate_step_edit,
    apply_edits,
)

# Errors
from .errors import (
    ExtractionError,
    ParseError,
    AmbiguityError,
    IncompleteError,
    categorize_error,
    format_errors_for_user,
)

# Validation
from .validation import (
    validate_algorithm,
    check_step_connectivity,
    check_variable_flow,
    ValidationResult,
)

__version__ = "0.1.0"

__all__ = [
    # Core types
    "Algorithm",
    "Step",
    "StepType",
    "algorithm_to_json",
    "algorithm_from_json",

    # Parsing
    "RuleBasedParser",
    "parse_algorithm",

    # LLM Extraction
    "HybridExtractor",
    "extract_algorithm_llm",
    "ExtractionResult",

    # Review
    "ReviewInterface",
    "validate_step_edit",
    "apply_edits",

    # Errors
    "ExtractionError",
    "ParseError",
    "AmbiguityError",
    "IncompleteError",
    "categorize_error",
    "format_errors_for_user",

    # Validation
    "validate_algorithm",
    "check_step_connectivity",
    "check_variable_flow",
    "ValidationResult",
]
