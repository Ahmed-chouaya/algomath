"""Tests for extraction error handling."""
import pytest
import json

from src.extraction.errors import (
    ExtractionError,
    ParseError,
    AmbiguityError,
    IncompleteError,
    categorize_error,
    format_errors_for_user,
)


class TestParseError:
    """Test ParseError functionality."""

    def test_parse_error_with_line(self):
        """Test ParseError with line number."""
        error = ParseError(
            message="unmatched parenthesis",
            line_number=5,
            suggestion="Check matching brackets"
        )

        assert "unmatched parenthesis" in str(error)
        assert "line 5" in str(error)
        assert "Check matching brackets" in str(error)
        assert error.line_number == 5

    def test_parse_error_to_dict(self):
        """Test ParseError serialization."""
        error = ParseError("syntax error", line_number=10)
        data = error.to_dict()

        assert data["type"] == "ParseError"
        assert data["line_number"] == 10


class TestAmbiguityError:
    """Test AmbiguityError functionality."""

    def test_ambiguity_error_with_interpretations(self):
        """Test AmbiguityError with multiple interpretations."""
        error = AmbiguityError(
            message="could mean assignment or function call",
            line_number=7,
            interpretations=["x = 5", "call x with 5"],
            suggestion="Clarify with explicit syntax"
        )

        assert "could mean" in str(error)
        assert error.interpretations == ["x = 5", "call x with 5"]

    def test_ambiguity_error_default_suggestion(self):
        """Test default suggestion."""
        error = AmbiguityError("unclear reference")
        assert "Provide more context" in str(error)


class TestIncompleteError:
    """Test IncompleteError functionality."""

    def test_incomplete_error_with_missing(self):
        """Test IncompleteError with missing items."""
        error = IncompleteError(
            message="missing return statement",
            line_number=20,
            missing=["return", "output variable"],
            suggestion="Add explicit return"
        )

        assert "missing return statement" in str(error)
        assert error.missing == ["return", "output variable"]

    def test_incomplete_error_default_suggestion(self):
        """Test default suggestion."""
        error = IncompleteError("truncated input")
        assert "Add missing information" in str(error)


class TestErrorCategorization:
    """Test error categorization."""

    def test_categorize_parse_error(self):
        """Test categorizing parse errors."""
        test_cases = [
            "unmatched bracket",
            "invalid syntax",
            "parse error at line 3",
            "unexpected token",
            "malformed expression",
        ]

        for text in test_cases:
            error = categorize_error(text, line_number=5)
            assert isinstance(error, ParseError)
            assert error.line_number == 5

    def test_categorize_ambiguity_error(self):
        """Test categorizing ambiguity errors."""
        test_cases = [
            "ambiguous reference",
            "could mean x or y",
            "unclear which variable",
            "multiple interpretations",
        ]

        for text in test_cases:
            error = categorize_error(text)
            assert isinstance(error, AmbiguityError)

    def test_categorize_incomplete_error(self):
        """Test categorizing incomplete errors."""
        test_cases = [
            "incomplete algorithm",
            "missing closing brace",
            "unexpected end of input",
            "truncated text",
        ]

        for text in test_cases:
            error = categorize_error(text, line_number=15)
            assert isinstance(error, IncompleteError)
            assert error.line_number == 15

    def test_categorize_generic_error(self):
        """Test fallback to generic error."""
        error = categorize_error("some random error")
        assert isinstance(error, ExtractionError)
        assert not isinstance(error, (ParseError, AmbiguityError, IncompleteError))


class TestErrorFormatting:
    """Test error formatting utilities."""

    def test_format_empty_errors(self):
        """Test formatting empty error list."""
        result = format_errors_for_user([])
        assert "No errors" in result

    def test_format_single_error(self):
        """Test formatting single error."""
        error = ParseError("test error", line_number=3)
        result = format_errors_for_user([error])

        assert "1." in result
        assert "test error" in result

    def test_format_multiple_errors(self):
        """Test formatting multiple errors."""
        errors = [
            ParseError("error 1", line_number=1),
            AmbiguityError("error 2", line_number=2),
            IncompleteError("error 3", line_number=3),
        ]
        result = format_errors_for_user(errors)

        assert "2." in result
        assert "3." in result
        assert "error 2" in result


class TestErrorEdgeCases:
    """Test edge cases for error handling."""

    def test_parse_error_without_line(self):
        """Test ParseError without line number."""
        error = ParseError("syntax error")
        assert error.line_number is None
        assert "syntax error" in str(error)

    def test_parse_error_without_suggestion(self):
        """Test ParseError uses default suggestion."""
        error = ParseError("parse failed")
        assert "Check syntax" in str(error)

    def test_ambiguity_error_empty_interpretations(self):
        """Test AmbiguityError with empty interpretations."""
        error = AmbiguityError("vague statement")
        assert error.interpretations == []

    def test_incomplete_error_empty_missing(self):
        """Test IncompleteError with empty missing list."""
        error = IncompleteError("incomplete")
        assert error.missing == []

    def test_extraction_error_base_class(self):
        """Test ExtractionError base functionality."""
        error = ExtractionError("base error", line_number=10)
        assert "base error" in str(error)
        assert "line 10" in str(error)

    def test_error_dict_serialization(self):
        """Test error to_dict for all types."""
        errors = [
            ParseError("parse", line_number=1),
            AmbiguityError("ambiguity", line_number=2),
            IncompleteError("incomplete", line_number=3),
        ]

        for error in errors:
            data = error.to_dict()
            assert "type" in data
            assert "message" in data
            assert "line_number" in data
            assert "suggestion" in data

    def test_error_dict_round_trip(self):
        """Test error dict can be JSON serialized."""
        error = ParseError("test", line_number=5)
        data = error.to_dict()
        json_str = json.dumps(data)
        restored = json.loads(json_str)

        assert restored["type"] == "ParseError"
        assert restored["line_number"] == 5


class TestErrorMessageFormatting:
    """Test error message formatting."""

    def test_message_with_all_fields(self):
        """Test message formatting with all fields."""
        error = ParseError(
            "unexpected token",
            line_number=10,
            suggestion="Check syntax"
        )
        msg = str(error)

        assert "Parse error" in msg
        assert "unexpected token" in msg
        assert "line 10" in msg
        assert "Suggestion" in msg

    def test_message_with_only_line(self):
        """Test message with only line number."""
        error = ParseError("error", line_number=3)
        msg = str(error)

        assert "(at line 3)" in msg
        assert "Suggestion" in msg  # Default suggestion

    def test_message_without_line(self):
        """Test message without line number."""
        error = ParseError("error")
        msg = str(error)

        assert "(at line" not in msg


class TestCategorizeEdgeCases:
    """Test edge cases in categorization."""

    def test_case_insensitive_matching(self):
        """Test that categorization is case insensitive."""
        errors = [
            categorize_error("UNMATCHED bracket"),
            categorize_error("Unmatched Bracket"),
            categorize_error("unmatched bracket"),
        ]

        for error in errors:
            assert isinstance(error, ParseError)

    def test_multiple_keywords_in_error(self):
        """Test error with multiple keywords."""
        error = categorize_error("unmatched parenthesis and missing bracket")
        # Should match first pattern found
        assert isinstance(error, (ParseError, IncompleteError))

    def test_empty_error_string(self):
        """Test categorizing empty string."""
        error = categorize_error("")
        assert isinstance(error, ExtractionError)

    def test_very_long_error_string(self):
        """Test categorizing very long error."""
        long_error = "parse error: " + "x" * 1000
        error = categorize_error(long_error)
        assert isinstance(error, ParseError)
