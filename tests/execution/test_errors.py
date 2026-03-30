"""Tests for error categorization and translation.

Covers EXE-05 (status reporting) and EXE-06 (meaningful error messages).
"""

import pytest
from subprocess import TimeoutExpired

from src.execution.errors import (
    ExecutionError,
    ErrorDetails,
    ErrorTranslator,
    categorize_error,
    extract_line_number,
)


class TestCategorizeError:
    """Test error categorization per D-17."""

    def test_categorize_syntax_error_from_exception(self):
        """Test 1: categorize_error() identifies SyntaxError from exception."""
        error = SyntaxError("invalid syntax")
        result = categorize_error(error)
        assert result == ExecutionError.SYNTAX_ERROR

    def test_categorize_timeout_error_from_subprocess(self):
        """Test 2: categorize_error() identifies TimeoutError from subprocess.TimeoutExpired."""
        error = TimeoutExpired(cmd="python test.py", timeout=30)
        result = categorize_error(error)
        assert result == ExecutionError.TIMEOUT_ERROR

    def test_categorize_memory_error_from_exception(self):
        """Test 3: categorize_error() identifies MemoryError from memory exceeded."""
        error = MemoryError("out of memory")
        result = categorize_error(error)
        assert result == ExecutionError.MEMORY_ERROR

    def test_categorize_runtime_error_for_general_exceptions(self):
        """Test 4: categorize_error() identifies RuntimeError for general exceptions."""
        error = ValueError("some value error")
        result = categorize_error(error)
        assert result == ExecutionError.RUNTIME_ERROR

    def test_categorize_syntax_error_from_stderr(self):
        """Test: categorize_error() identifies SyntaxError from stderr content."""
        error = Exception("execution failed")
        stderr = "Traceback (most recent call last):\n  File \"test.py\", line 5\n    if x = 5\n         ^\nSyntaxError: invalid syntax"
        result = categorize_error(error, stderr)
        assert result == ExecutionError.SYNTAX_ERROR

    def test_categorize_memory_error_from_stderr(self):
        """Test: categorize_error() identifies MemoryError from stderr content."""
        error = Exception("execution failed")
        stderr = "MemoryError: Unable to allocate array"
        result = categorize_error(error, stderr)
        assert result == ExecutionError.MEMORY_ERROR


class TestErrorTranslator:
    """Test error translation per D-18 and D-20."""

    def test_translate_syntax_error_has_user_friendly_message(self):
        """Test 5: ErrorTranslator.translate() returns user-friendly message per D-18."""
        result = ErrorTranslator.translate(ExecutionError.SYNTAX_ERROR)
        assert "syntax" in result.user_message.lower()
        assert "SyntaxError" not in result.user_message

    def test_translate_timeout_error_has_user_friendly_message(self):
        """Test: ErrorTranslator.translate() returns user-friendly timeout message."""
        result = ErrorTranslator.translate(ExecutionError.TIMEOUT_ERROR)
        assert "too long" in result.user_message.lower() or "time" in result.user_message.lower()
        assert "TimeoutExpired" not in result.user_message

    def test_translate_memory_error_has_user_friendly_message(self):
        """Test: ErrorTranslator.translate() returns user-friendly memory message."""
        result = ErrorTranslator.translate(ExecutionError.MEMORY_ERROR)
        assert "memory" in result.user_message.lower()
        assert "MemoryError" not in result.user_message

    def test_translate_runtime_error_has_user_friendly_message(self):
        """Test: ErrorTranslator.translate() returns user-friendly runtime message."""
        result = ErrorTranslator.translate(ExecutionError.RUNTIME_ERROR)
        assert "error" in result.user_message.lower()

    def test_translate_includes_hint_per_d20(self):
        """Test 6: ErrorTranslator.translate() includes hint per D-20."""
        result = ErrorTranslator.translate(ExecutionError.SYNTAX_ERROR)
        assert result.hint
        assert len(result.hint) > 0

    def test_translate_syntax_error_hint_suggests_regeneration(self):
        """Test: SyntaxError hint suggests regeneration."""
        result = ErrorTranslator.translate(ExecutionError.SYNTAX_ERROR)
        assert "regenerat" in result.hint.lower() or "translation" in result.hint.lower()

    def test_translate_timeout_error_hint_suggests_loop_check(self):
        """Test: TimeoutError hint suggests checking loops."""
        result = ErrorTranslator.translate(ExecutionError.TIMEOUT_ERROR)
        assert "loop" in result.hint.lower() or "infinite" in result.hint.lower() or "optim" in result.hint.lower()

    def test_translate_preserves_technical_details(self):
        """Test: Translation preserves technical details for debugging."""
        technical = "Traceback: line 42, in function\nValueError: invalid value"
        result = ErrorTranslator.translate(ExecutionError.RUNTIME_ERROR, technical)
        assert result.technical_details == technical


class TestExtractLineNumber:
    """Test line number extraction per D-19."""

    def test_extract_line_number_from_traceback(self):
        """Test 7: get_technical_details() extracts Python traceback line number."""
        traceback = """Traceback (most recent call last):
  File "test.py", line 15, in <module>
    result = fibonacci(n)
  File "test.py", line 8, in fibonacci
    return fibonacci(n-1) + fibonacci(n-2)
RecursionError: maximum recursion depth exceeded"""
        result = extract_line_number(traceback)
        assert result == 15

    def test_extract_line_number_returns_none_for_invalid_traceback(self):
        """Test: extract_line_number returns None for invalid traceback."""
        traceback = "Some error without line number"
        result = extract_line_number(traceback)
        assert result is None

    def test_extract_line_number_handles_empty_string(self):
        """Test: extract_line_number handles empty string."""
        result = extract_line_number("")
        assert result is None


class TestErrorDetailsDataclass:
    """Test ErrorDetails dataclass per D-19."""

    def test_error_details_has_required_fields(self):
        """Test: ErrorDetails has all required fields per D-19."""
        details = ErrorDetails(
            category=ExecutionError.SYNTAX_ERROR,
            user_message="Generated code has a syntax issue",
            hint="Try regenerating",
            technical_details="SyntaxError: invalid syntax",
            line_number=42
        )
        assert details.category == ExecutionError.SYNTAX_ERROR
        assert details.user_message == "Generated code has a syntax issue"
        assert details.hint == "Try regenerating"
        assert details.technical_details == "SyntaxError: invalid syntax"
        assert details.line_number == 42

    def test_error_details_technical_details_optional(self):
        """Test: technical_details is optional in ErrorDetails."""
        details = ErrorDetails(
            category=ExecutionError.SUCCESS,
            user_message="Success",
            hint="No issues"
        )
        assert details.technical_details is None

    def test_error_details_line_number_optional(self):
        """Test: line_number is optional in ErrorDetails."""
        details = ErrorDetails(
            category=ExecutionError.SUCCESS,
            user_message="Success",
            hint="No issues"
        )
        assert details.line_number is None
