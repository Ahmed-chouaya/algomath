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
]
