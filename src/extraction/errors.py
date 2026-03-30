"""Extraction error types for AlgoMath."""
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class ExtractionError(Exception):
    """Base class for extraction errors."""

    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None

    def __str__(self) -> str:
        parts = [self.message]
        if self.line_number:
            parts.append(f" (at line {self.line_number})")
        if self.suggestion:
            parts.append(f"\nSuggestion: {self.suggestion}")
        return "".join(parts)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "line_number": self.line_number,
            "suggestion": self.suggestion
        }


class ParseError(ExtractionError):
    """
    Raised when text cannot be parsed.

    Per D-23 from 02-CONTEXT.md.
    """

    def __init__(self, message: str, line_number: Optional[int] = None,
                 suggestion: Optional[str] = None):
        super().__init__(
            message=f"Parse error: {message}",
            line_number=line_number,
            suggestion=suggestion or "Check syntax and try again"
        )


class AmbiguityError(ExtractionError):
    """
    Raised when multiple valid interpretations exist.

    Per D-23 from 02-CONTEXT.md.
    """

    def __init__(self, message: str, line_number: Optional[int] = None,
                 interpretations: Optional[List[str]] = None,
                 suggestion: Optional[str] = None):
        super().__init__(
            message=f"Ambiguity: {message}",
            line_number=line_number,
            suggestion=suggestion or "Provide more context"
        )
        self.interpretations = interpretations or []


class IncompleteError(ExtractionError):
    """
    Raised when algorithm appears incomplete.

    Per D-23 from 02-CONTEXT.md.
    """

    def __init__(self, message: str, line_number: Optional[int] = None,
                 missing: Optional[List[str]] = None,
                 suggestion: Optional[str] = None):
        super().__init__(
            message=f"Incomplete: {message}",
            line_number=line_number,
            suggestion=suggestion or "Add missing information"
        )
        self.missing = missing or []


def categorize_error(error_text: str, line_number: Optional[int] = None) -> ExtractionError:
    """
    Categorize an error message into appropriate error type.

    Args:
        error_text: Raw error message
        line_number: Line where error occurred

    Returns:
        Categorized ExtractionError

    Per D-23 from 02-CONTEXT.md.
    """
    text_lower = error_text.lower()

    # Parse errors
    parse_patterns = [
        "unmatched", "unexpected", "invalid syntax", "parse",
        "cannot parse", "syntax error", "malformed"
    ]
    if any(p in text_lower for p in parse_patterns):
        return ParseError(
            message=error_text,
            line_number=line_number,
            suggestion="Check for matching parentheses, brackets, or quotes"
        )

    # Ambiguity errors
    ambiguity_patterns = [
        "ambiguous", "could mean", "could be", "unclear",
        "multiple interpretations", "not sure if", "could refer to"
    ]
    if any(p in text_lower for p in ambiguity_patterns):
        return AmbiguityError(
            message=error_text,
            line_number=line_number,
            suggestion="Clarify the meaning with more specific language"
        )

    # Incomplete errors
    incomplete_patterns = [
        "incomplete", "missing", "not found", "expected",
        "end of input", "unexpected end", "truncated"
    ]
    if any(p in text_lower for p in incomplete_patterns):
        return IncompleteError(
            message=error_text,
            line_number=line_number,
            suggestion="Ensure the algorithm has a complete description"
        )

    # Default to generic extraction error
    return ExtractionError(
        message=error_text,
        line_number=line_number,
        suggestion="Review the text and try again"
    )


def format_errors_for_user(errors: List[ExtractionError]) -> str:
    """
    Format multiple errors into user-friendly message.

    Per D-24 from 02-CONTEXT.md.
    """
    if not errors:
        return "No errors found."

    lines = ["Extraction completed with issues:"]
    for i, error in enumerate(errors, 1):
        lines.append(f"\n{i}. {error}")

    return "\n".join(lines)
