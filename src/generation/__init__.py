"""Code generation module for AlgoMath.

This module provides tools for converting structured algorithms
into executable Python code.
"""

from src.generation.types import (
    TypeInferrer,
    PythonType,
    FunctionSignature,
    ValidationResult,
)
from src.generation.templates import (
    TemplateRegistry,
    CodeTemplates,
)
from src.generation.code_generator import (
    TemplateCodeGenerator,
    GeneratedCode,
)
from src.generation.llm_generator import (
    LLMCodeGenerator,
)
from src.generation.hybrid import (
    HybridCodeGenerator,
    HybridGenerationResult,
)
from src.generation.errors import (
    GenerationError,
    SyntaxGenerationError,
    ImportGenerationError,
    LLMGenerationError,
    ValidationError,
)
from src.generation.validation import (
    ValidationResult,
    CodeValidator,
)
from src.generation.review import (
    CodeReviewInterface,
    ReviewState,
    create_review,
)
from src.generation.persistence import (
    CodePersistence,
    save_to_context,
)

__all__ = [
    # Types
    "TypeInferrer",
    "PythonType",
    "FunctionSignature",
    "ValidationResult",
    # Templates
    "TemplateRegistry",
    "CodeTemplates",
    # Generators
    "TemplateCodeGenerator",
    "LLMCodeGenerator",
    "HybridCodeGenerator",
    "HybridGenerationResult",
    "GeneratedCode",
    # Errors
    "GenerationError",
    "SyntaxGenerationError",
    "ImportGenerationError",
    "LLMGenerationError",
    "ValidationError",
    # Validation
    "CodeValidator",
    # Review
    "CodeReviewInterface",
    "ReviewState",
    "create_review",
    # Persistence
    "CodePersistence",
    "save_to_context",
]
