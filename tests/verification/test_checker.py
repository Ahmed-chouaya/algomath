"""Tests for execution verification checker.

Per VER-01: Verify execution completed without errors.
Covers TDD behaviors for Task 1 of 05-01-PLAN.md.
"""

import json
import pytest
from datetime import datetime
from src.verification.checker import (
    VerificationStatus,
    VerificationResult,
    ExecutionChecker,
    verify_execution,
)


class TestVerificationStatus:
    """Test VerificationStatus enum."""

    def test_status_values_exist(self):
        """Test that all status values are defined."""
        assert VerificationStatus.SUCCESS.value == 'success'
        assert VerificationStatus.FAILED.value == 'failed'
        assert VerificationStatus.ERROR.value == 'error'
        assert VerificationStatus.INCOMPLETE.value == 'incomplete'


class TestVerificationResult:
    """Test VerificationResult dataclass."""

    def test_result_creation(self):
        """Test 4: VerificationResult contains execution metadata."""
        result = VerificationResult(
            status=VerificationStatus.SUCCESS,
            message="All checks passed",
            checks_performed=["no_errors", "output_present"],
            execution_summary="Algorithm completed successfully.",
            runtime_seconds=1.5,
            output_size=42,
            timestamp="2026-03-30T22:00:00Z"
        )
        assert result.status == VerificationStatus.SUCCESS
        assert result.runtime_seconds == 1.5
        assert result.output_size == 42

    def test_result_to_dict(self):
        """Test 5: VerificationResult is JSON-serializable."""
        result = VerificationResult(
            status=VerificationStatus.SUCCESS,
            message="All checks passed",
            checks_performed=["no_errors", "output_present"],
            execution_summary="Algorithm completed successfully.",
            runtime_seconds=1.5,
            output_size=42,
            timestamp="2026-03-30T22:00:00Z"
        )
        result_dict = result.to_dict()
        assert result_dict['status'] == 'success'
        assert result_dict['runtime_seconds'] == 1.5
        assert result_dict['output_size'] == 42

    def test_result_to_json(self):
        """Test 5: VerificationResult can be serialized to JSON."""
        result = VerificationResult(
            status=VerificationStatus.SUCCESS,
            message="All checks passed",
            checks_performed=["no_errors", "output_present"],
            execution_summary="Algorithm completed successfully.",
            runtime_seconds=1.5,
            output_size=42,
            timestamp="2026-03-30T22:00:00Z"
        )
        json_str = result.to_json()
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed['status'] == 'success'
        assert parsed['runtime_seconds'] == 1.5


class TestExecutionChecker:
    """Test ExecutionChecker class."""

    def test_checker_initialization(self):
        """Test that ExecutionChecker can be initialized."""
        results = {'status': 'success', 'stdout': 'test', 'runtime_seconds': 1.5}
        checker = ExecutionChecker(results)
        assert checker.results == results

    def test_check_returns_verification_result(self):
        """Test 1: check() returns VerificationResult for valid execution."""
        results = {
            'status': 'success',
            'stdout': 'output here',
            'stderr': '',
            'runtime_seconds': 1.5,
            'return_value': None
        }
        checker = ExecutionChecker(results)
        result = checker.check()
        assert isinstance(result, VerificationResult)
        assert result.status == VerificationStatus.SUCCESS

    def test_check_returns_failure_for_timeout(self):
        """Test 2: check() returns failure for timeout status."""
        results = {
            'status': 'timeout',
            'stdout': '',
            'stderr': 'Timeout occurred',
            'runtime_seconds': 30.0,
            'error_type': 'TimeoutExpired',
            'error_message': 'Execution timed out'
        }
        checker = ExecutionChecker(results)
        result = checker.check()
        assert result.status == VerificationStatus.FAILED

    def test_check_returns_failure_for_error_status(self):
        """Test 2: check() returns failure for error status."""
        results = {
            'status': 'error',
            'stdout': '',
            'stderr': 'Traceback...',
            'runtime_seconds': 0.5,
            'error_type': 'RuntimeError',
            'error_message': 'Something went wrong'
        }
        checker = ExecutionChecker(results)
        result = checker.check()
        assert result.status == VerificationStatus.ERROR

    def test_no_errors_check_passes(self):
        """Test internal _check_no_errors method."""
        results = {'status': 'success', 'stdout': 'test', 'runtime_seconds': 1.0}
        checker = ExecutionChecker(results)
        passed, message = checker._check_no_errors()
        assert passed is True
        assert 'success' in message.lower()

    def test_no_errors_check_fails(self):
        """Test internal _check_no_errors method for failures."""
        results = {'status': 'timeout', 'stdout': '', 'runtime_seconds': 30.0}
        checker = ExecutionChecker(results)
        passed, message = checker._check_no_errors()
        assert passed is False

    def test_output_present_check_passes(self):
        """Test internal _check_output_present method."""
        results = {'status': 'success', 'stdout': 'some output', 'runtime_seconds': 1.0}
        checker = ExecutionChecker(results)
        passed, message = checker._check_output_present()
        assert passed is True

    def test_output_present_check_fails(self):
        """Test internal _check_output_present method for empty output."""
        results = {'status': 'success', 'stdout': '', 'runtime_seconds': 1.0}
        checker = ExecutionChecker(results)
        passed, message = checker._check_output_present()
        assert passed is False

    def test_execution_summary_generation(self):
        """Test 4: VerificationResult contains execution summary."""
        results = {
            'status': 'success',
            'stdout': 'line1\nline2\nline3',
            'runtime_seconds': 2.5
        }
        checker = ExecutionChecker(results)
        result = checker.check()
        assert len(result.execution_summary) > 0
        assert '3' in result.execution_summary or 'line' in result.execution_summary.lower()


class TestVerifyExecution:
    """Test verify_execution function."""

    def test_verify_execution_returns_result(self):
        """Test 3: verify_execution() returns VerificationResult."""
        results = {
            'status': 'success',
            'stdout': 'test output',
            'runtime_seconds': 1.0
        }
        result = verify_execution(results)
        assert isinstance(result, VerificationResult)
        assert result.status == VerificationStatus.SUCCESS

    def test_verify_execution_includes_checks_performed(self):
        """Test 3: verify_execution() includes checks_performed list."""
        results = {
            'status': 'success',
            'stdout': 'test output',
            'runtime_seconds': 1.0
        }
        result = verify_execution(results)
        assert len(result.checks_performed) > 0
        assert isinstance(result.checks_performed, list)

    def test_verify_execution_with_error(self):
        """Test 3: verify_execution() handles error results."""
        results = {
            'status': 'runtime_error',
            'stdout': '',
            'stderr': 'Error occurred',
            'runtime_seconds': 0.5
        }
        result = verify_execution(results)
        assert result.status in [VerificationStatus.FAILED, VerificationStatus.ERROR]


class TestSummaryGeneration:
    """Test summary generation per D-05."""

    def test_success_summary_format(self):
        """Test summary format for successful execution per D-05."""
        results = {
            'status': 'success',
            'stdout': 'line1\nline2\nline3',
            'runtime_seconds': 2.5
        }
        checker = ExecutionChecker(results)
        summary = checker._generate_summary()
        # Should be 1-2 sentences
        assert len(summary.split('.')) <= 3  # 2 sentences + possibly empty
        assert '3' in summary or 'output' in summary.lower()

    def test_failure_summary_format(self):
        """Test summary format for failed execution per D-05."""
        results = {
            'status': 'timeout',
            'stdout': '',
            'runtime_seconds': 30.0
        }
        checker = ExecutionChecker(results)
        summary = checker._generate_summary()
        assert 'timeout' in summary.lower() or 'failed' in summary.lower() or 'after' in summary.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
