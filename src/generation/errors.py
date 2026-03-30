"""Error classes for code generation.

This module defines the error hierarchy for generation failures.
"""

from typing import Optional


class GenerationError(Exception):
    """Base class for generation errors."""
    
    def __init__(self, message: str, 
                 line_number: Optional[int] = None,
                 context: Optional[str] = None):
        self.message = message
        self.line_number = line_number
        self.context = context
        super().__init__(self.format_message())
    
    def format_message(self) -> str:
        """Format error message for display."""
        if self.line_number:
            return f"Generation error at line {self.line_number}: {self.message}"
        return f"Generation error: {self.message}"


class SyntaxGenerationError(GenerationError):
    """Raised when generated code has syntax errors."""
    pass


class ImportGenerationError(GenerationError):
    """Raised when generated code has unresolved imports."""
    pass


class UnsupportedConstructError(GenerationError):
    """Raised when step contains unsupported construct."""
    pass


class LLMGenerationError(GenerationError):
    """Raised when LLM fails to generate code."""
    pass


class ValidationError(GenerationError):
    """Raised when generated code fails validation."""
    pass


def format_error_for_user(error: GenerationError) -> str:
    """
    Format error message for user display.
    
    Args:
        error: GenerationError to format
        
    Returns:
        Formatted error string
    """
    lines = []
    lines.append(f"Code Generation Error: {error.message}")
    
    if error.line_number:
        lines.append(f"  Location: Line {error.line_number}")
    
    if error.context:
        lines.append(f"  Context: {error.context}")
    
    lines.append("\n  Suggestion: Check the algorithm steps and try again.")
    
    return '\n'.join(lines)


__all__ = [
    "GenerationError",
    "SyntaxGenerationError",
    "ImportGenerationError",
    "UnsupportedConstructError",
    "LLMGenerationError",
    "ValidationError",
    "format_error_for_user",
]
