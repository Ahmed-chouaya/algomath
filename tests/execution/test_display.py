"""Tests for output formatting and display.

Covers EXE-05 (status reporting) and output formatting per D-13 through D-16.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from src.execution.display import (
    truncate_output,
    ExecutionFormatter,
    show_execution_summary,
    show_progress,
    FormattedResult,
)
from src.execution.errors import ExecutionError, ErrorTranslator


class TestTruncateOutput:
    """Test output truncation per D-15."""

    def test_truncate_output_under_50_lines_no_truncation(self):
        """Test 1: format_output() truncates >50 lines per D-15."""
        text = "Line 1\nLine 2\nLine 3"
        result = truncate_output(text, max_lines=50)
        assert result == text

    def test_truncate_output_over_50_lines_truncates(self):
        """Test: Output over 50 lines gets truncated."""
        text = "\n".join([f"Line {i}" for i in range(60)])
        result = truncate_output(text, max_lines=50)
        assert "... (10 more lines" in result
        assert len(result.split('\n')) == 51  # 50 lines + truncation message

    def test_truncate_output_shows_summary(self):
        """Test 2: format_output() shows summary with line count for truncated output."""
        text = "\n".join([f"Line {i}" for i in range(100)])
        result = truncate_output(text, max_lines=50)
        assert "(50 more lines" in result


class TestShowProgress:
    """Test progress indicators per D-23."""

    def test_progress_format_matches_phase1_pattern(self):
        """Test 5: Progress indicator format matches Phase 1 pattern."""
        result = show_progress("Execute", 5, 10)
        # Should be like "Execute: █████░░░░░ 50%"
        assert result.startswith("Execute: ")
        assert "50%" in result or "40%" in result or "60%" in result
        assert "█" in result
        assert "░" in result

    def test_progress_zero_percent(self):
        """Test: Zero percent progress."""
        result = show_progress("Execute", 0, 10)
        assert "0%" in result

    def test_progress_100_percent(self):
        """Test: 100 percent progress."""
        result = show_progress("Execute", 10, 10)
        assert "100%" in result or "90%" in result
        assert "██████████" in result or "░░░░░░░░░░" not in result


class TestExecutionFormatter:
    """Test execution result formatting per D-14, D-16."""

    def test_format_results_returns_formatted_result(self):
        """Test: ExecutionFormatter returns FormattedResult."""
        formatter = ExecutionFormatter(algorithm_name="test_algo")
        mock_result = Mock()
        mock_result.status = 'success'
        mock_result.runtime_seconds = 1.234
        mock_result.stdout = "Output line 1\nOutput line 2"
        mock_result.stderr = ""

        result = formatter.format_results(mock_result)
        assert isinstance(result, FormattedResult)

    def test_format_results_success_status(self):
        """Test: Success status shows checkmark."""
        formatter = ExecutionFormatter(algorithm_name="test_algo")
        mock_result = Mock()
        mock_result.status = 'success'
        mock_result.runtime_seconds = 1.234
        mock_result.stdout = "Output"
        mock_result.stderr = ""

        result = formatter.format_results(mock_result)
        assert result.status_emoji == '✓'
        assert result.status_text == 'Success'

    def test_format_results_failure_status(self):
        """Test: Failure status shows X mark."""
        formatter = ExecutionFormatter(algorithm_name="test_algo")
        mock_result = Mock()
        mock_result.status = 'error'
        mock_result.runtime_seconds = 0.5
        mock_result.stdout = ""
        mock_result.stderr = "Error message"

        result = formatter.format_results(mock_result)
        assert result.status_emoji == '✗'
        assert result.status_text == 'Failed'

    def test_format_results_timeout_status(self):
        """Test: Timeout status shows clock."""
        formatter = ExecutionFormatter(algorithm_name="test_algo")
        mock_result = Mock()
        mock_result.status = 'timeout'
        mock_result.runtime_seconds = 30.0
        mock_result.stdout = ""
        mock_result.stderr = ""

        result = formatter.format_results(mock_result)
        assert result.status_emoji == '⏱'
        assert result.status_text == 'Timed Out'

    def test_format_results_includes_execution_time(self):
        """Test 4: ExecutionFormatter includes execution time prominently."""
        formatter = ExecutionFormatter(algorithm_name="test_algo")
        mock_result = Mock()
        mock_result.status = 'success'
        mock_result.runtime_seconds = 1.234
        mock_result.stdout = ""
        mock_result.stderr = ""

        result = formatter.format_results(mock_result)
        assert '1.234' in result.execution_time
        assert 'Time:' in result.display_text or 'execution' in result.display_text.lower()

    def test_format_results_truncates_long_output(self):
        """Test: Long output gets truncated."""
        formatter = ExecutionFormatter(algorithm_name="test_algo")
        mock_result = Mock()
        mock_result.status = 'success'
        mock_result.runtime_seconds = 0.1
        mock_result.stdout = "\n".join([f"Line {i}" for i in range(60)])
        mock_result.stderr = ""

        result = formatter.format_results(mock_result)
        assert result.output_truncated is True

    def test_format_results_includes_log_path(self):
        """Test: Full log path included for truncated output."""
        formatter = ExecutionFormatter(algorithm_name="test_algo")
        mock_result = Mock()
        mock_result.status = 'success'
        mock_result.runtime_seconds = 0.1
        mock_result.stdout = "\n".join([f"Line {i}" for i in range(60)])
        mock_result.stderr = ""

        result = formatter.format_results(mock_result)
        assert ".algomath/algorithms/test_algo/execution.log" in result.display_text


class TestShowExecutionSummary:
    """Test execution summary display per D-14, EXE-05, EXE-06."""

    def test_show_execution_summary_success(self):
        """Test 3: show_execution_summary() displays status clearly per D-14."""
        mock_result = Mock()
        mock_result.status = 'success'
        mock_result.runtime_seconds = 1.5

        summary = show_execution_summary(mock_result)
        assert '✓' in summary or 'success' in summary.lower()
        assert '1.5' in summary or '1.500' in summary

    def test_show_execution_summary_failure_with_error(self):
        """Test: Failure summary includes error info."""
        mock_result = Mock()
        mock_result.status = 'error'
        mock_result.runtime_seconds = 0.5

        error_details = ErrorTranslator.translate(ExecutionError.SYNTAX_ERROR, "SyntaxError")
        summary = show_execution_summary(mock_result, error_details)
        assert '✗' in summary or 'error' in summary.lower()
        assert 'syntax' in summary.lower()

    def test_show_execution_summary_includes_user_message(self):
        """Test: Summary includes user-friendly error message."""
        mock_result = Mock()
        mock_result.status = 'error'
        mock_result.runtime_seconds = 0.5

        error_details = ErrorTranslator.translate(ExecutionError.RUNTIME_ERROR, "ValueError")
        summary = show_execution_summary(mock_result, error_details)
        assert error_details.user_message in summary

    def test_show_execution_summary_includes_hint(self):
        """Test: Summary includes hint per D-20."""
        mock_result = Mock()
        mock_result.status = 'error'
        mock_result.runtime_seconds = 0.5

        error_details = ErrorTranslator.translate(ExecutionError.TIMEOUT_ERROR)
        summary = show_execution_summary(mock_result, error_details)
        assert error_details.hint in summary

    def test_show_execution_summary_includes_technical_details(self):
        """Test 6: Error display includes user message + hint + collapsed technical details."""
        mock_result = Mock()
        mock_result.status = 'error'
        mock_result.runtime_seconds = 0.5

        technical = "Traceback:\n  File test.py, line 10\nValueError"
        error_details = ErrorTranslator.translate(ExecutionError.RUNTIME_ERROR, technical)
        summary = show_execution_summary(mock_result, error_details)
        assert '<details>' in summary or technical in summary

    def test_show_execution_summary_no_error_details_for_success(self):
        """Test: Success summary without error details is clean."""
        mock_result = Mock()
        mock_result.status = 'success'
        mock_result.runtime_seconds = 2.0

        summary = show_execution_summary(mock_result, None)
        assert 'success' in summary.lower()


class TestFormattedResult:
    """Test FormattedResult dataclass."""

    def test_formatted_result_has_required_fields(self):
        """Test: FormattedResult has all required fields per D-14, D-16."""
        result = FormattedResult(
            display_text="Execution complete",
            status_emoji='✓',
            status_text='Success',
            execution_time='1.5s',
            output_truncated=False,
            full_log_path=None
        )
        assert result.display_text == "Execution complete"
        assert result.status_emoji == '✓'
        assert result.status_text == 'Success'
        assert result.execution_time == '1.5s'
        assert result.output_truncated is False
        assert result.full_log_path is None
