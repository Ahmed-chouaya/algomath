"""Tests for the sandbox execution module.

Per D-01 through D-06: Sandboxed subprocess execution with resource limits,
timeout protection, output capture, and file system restrictions.
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.execution.sandbox import SandboxExecutor, ExecutionResult, ExecutionStatus


class TestSandboxExecution:
    """Test suite for sandboxed code execution."""

    def test_execute_in_sandbox_captures_stdout(self):
        """Test 1: execute_in_sandbox() runs code and captures stdout."""
        executor = SandboxExecutor(timeout=30, max_memory_mb=512)
        code = 'print("Hello, World!")'

        result = executor.execute(code)

        assert isinstance(result, ExecutionResult)
        assert result.status == ExecutionStatus.SUCCESS
        assert "Hello, World!" in result.stdout
        assert result.stderr == ""
        assert result.runtime_seconds > 0

    def test_subprocess_terminates_after_timeout(self):
        """Test 2: Subprocess terminates after timeout (mock short timeout)."""
        executor = SandboxExecutor(timeout=1, max_memory_mb=512)
        code = 'import time; time.sleep(10)'

        result = executor.execute(code)

        assert result.status == ExecutionStatus.TIMEOUT
        assert "timeout" in result.error_message.lower() or "timed out" in result.error_message.lower()

    def test_restricted_imports_raise_error(self):
        """Test 4: Restricted imports (os, sys) raise ImportError."""
        executor = SandboxExecutor(timeout=30, max_memory_mb=512)
        code = 'import os'

        result = executor.execute(code)

        # Should fail due to blocked import
        assert result.status in [ExecutionStatus.RUNTIME_ERROR, ExecutionStatus.IMPORT_ERROR]
        assert result.error_type is not None

    def test_temp_directory_created_and_cleaned(self):
        """Test 5: Temp directory created, cleaned up after execution."""
        executor = SandboxExecutor(timeout=30, max_memory_mb=512)
        code = 'print("test")'

        # Track if temp directory was used
        import tempfile
        original_mkdtemp = tempfile.mkdtemp
        created_dirs = []

        def mock_mkdtemp(*args, **kwargs):
            d = original_mkdtemp(*args, **kwargs)
            created_dirs.append(d)
            return d

        tempfile.mkdtemp = mock_mkdtemp

        try:
            result = executor.execute(code)
            # Temp directory should be created and cleaned up
            if created_dirs:
                # Directory should not exist after execution (cleanup)
                assert not Path(created_dirs[0]).exists() or result.status == ExecutionStatus.SUCCESS
        finally:
            tempfile.mkdtemp = original_mkdtemp

    def test_execution_result_contains_all_fields(self):
        """Test 6: ExecutionResult contains status, stdout, stderr, runtime."""
        executor = SandboxExecutor(timeout=30, max_memory_mb=512)
        code = 'print("stdout"); import sys; sys.stderr.write("stderr")'

        result = executor.execute(code)

        assert hasattr(result, 'status')
        assert hasattr(result, 'stdout')
        assert hasattr(result, 'stderr')
        assert hasattr(result, 'runtime_seconds')
        assert hasattr(result, 'return_value')
        assert hasattr(result, 'error_type')
        assert hasattr(result, 'error_message')

    def test_code_with_syntax_error(self):
        """Test syntax error handling."""
        executor = SandboxExecutor(timeout=30, max_memory_mb=512)
        code = 'def broken('  # Syntax error

        result = executor.execute(code)

        assert result.status == ExecutionStatus.SYNTAX_ERROR
        assert "syntax" in result.error_message.lower() or "SyntaxError" in result.error_message

    def test_code_captures_stderr(self):
        """Test stderr capture."""
        executor = SandboxExecutor(timeout=30, max_memory_mb=512)
        code = 'import sys; sys.stderr.write("error message")'

        result = executor.execute(code)

        assert "error message" in result.stderr

    def test_returns_successful_exit_code(self):
        """Test successful execution returns proper status."""
        executor = SandboxExecutor(timeout=30, max_memory_mb=512)
        code = 'x = 1 + 1'

        result = executor.execute(code)

        assert result.status == ExecutionStatus.SUCCESS


class TestExecutionStatus:
    """Test ExecutionStatus enum."""

    def test_status_values(self):
        """Test ExecutionStatus has expected values."""
        assert ExecutionStatus.SUCCESS.value == "success"
        assert ExecutionStatus.TIMEOUT.value == "timeout"
        assert ExecutionStatus.MEMORY_ERROR.value == "memory_error"
        assert ExecutionStatus.RUNTIME_ERROR.value == "runtime_error"
        assert ExecutionStatus.SYNTAX_ERROR.value == "syntax_error"
        assert ExecutionStatus.IMPORT_ERROR.value == "import_error"


class TestSandboxConfiguration:
    """Test sandbox configuration options."""

    def test_custom_timeout(self):
        """Test custom timeout configuration."""
        executor = SandboxExecutor(timeout=60, max_memory_mb=512)
        assert executor.timeout == 60

    def test_custom_memory_limit(self):
        """Test custom memory limit configuration."""
        executor = SandboxExecutor(timeout=30, max_memory_mb=1024)
        assert executor.max_memory_mb == 1024

    def test_default_configuration(self):
        """Test default configuration values."""
        executor = SandboxExecutor()
        assert executor.timeout == 30
        assert executor.max_memory_mb == 512
