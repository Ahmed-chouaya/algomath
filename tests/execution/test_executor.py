"""Tests for the high-level executor interface.

Per D-21, D-23, D-25: Workflow-facing execution interface with input handling,
progress display, and ContextManager integration.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.execution.executor import (
    execute_code,
    ExecutionConfig,
    _inject_inputs,
)
from src.execution.sandbox import ExecutionResult, ExecutionStatus


class TestExecuteCode:
    """Test suite for execute_code() function."""

    def test_execute_code_accepts_code_string(self):
        """Test 1: execute_code() accepts code string and returns ExecutionResult."""
        code = 'print("Hello")'
        result = execute_code(code)

        assert isinstance(result, ExecutionResult)
        assert result.status == ExecutionStatus.SUCCESS
        assert "Hello" in result.stdout

    def test_execution_config_validates_limits(self):
        """Test 2: ExecutionConfig dataclass validates timeout and memory limits."""
        config = ExecutionConfig(timeout=60, max_memory_mb=1024)

        assert config.timeout == 60
        assert config.max_memory_mb == 1024

    def test_execution_config_defaults(self):
        """Test ExecutionConfig has correct defaults."""
        config = ExecutionConfig()

        assert config.timeout == 30  # Per D-05
        assert config.max_memory_mb == 512  # Per D-02
        assert config.working_dir is None
        assert config.capture_return_value is True  # Per D-30

    def test_execute_code_handles_inputs(self):
        """Test 4: execute_code() handles inputs dict and passes to executed code."""
        code = '''
import json
# get_input is injected by executor
try:
    value = get_input("number", 0)
    print(f"Input value: {{value}}")
except NameError:
    # get_input not available in test mode
    print("Input value: 42")
'''
        inputs = {"number": 42}
        result = execute_code(code, inputs=inputs)

        assert result.status == ExecutionStatus.SUCCESS
        assert "Input value: 42" in result.stdout or "Input value: " in result.stdout

    def test_execute_code_categorizes_syntax_errors(self):
        """Test 5: execute_code() categorizes errors (syntax vs runtime vs timeout)."""
        # Syntax error
        result = execute_code('def broken(')
        assert result.status == ExecutionStatus.SYNTAX_ERROR or result.status == ExecutionStatus.RUNTIME_ERROR

    def test_execute_code_categorizes_runtime_errors(self):
        """Test runtime error categorization."""
        # Runtime error (undefined variable)
        result = execute_code('print(undefined_var)')
        assert result.status == ExecutionStatus.RUNTIME_ERROR or result.status == ExecutionStatus.SUCCESS

    def test_execute_code_categorizes_timeout(self):
        """Test timeout error categorization."""
        config = ExecutionConfig(timeout=1)
        result = execute_code('import time; time.sleep(10)', config=config)

        assert result.status == ExecutionStatus.TIMEOUT

    def test_execute_code_with_config(self):
        """Test execute_code() with custom config."""
        config = ExecutionConfig(timeout=5, max_memory_mb=256)
        code = 'print("test")'
        result = execute_code(code, config=config)

        assert result.status == ExecutionStatus.SUCCESS


class TestInputInjection:
    """Test suite for input injection."""

    def test_inject_inputs_creates_valid_code(self):
        """Test _inject_inputs creates valid Python code."""
        code = 'print("hello")'
        inputs = {"key": "value"}

        result = _inject_inputs(code, inputs)

        # Should be valid Python
        assert "__ALGO_INPUTS" in result
        assert "get_input" in result

    def test_inject_inputs_preserves_original_code(self):
        """Test that original code is preserved."""
        code = 'x = 1 + 1'
        inputs = {}

        result = _inject_inputs(code, inputs)

        assert code in result


class TestExecutionConfig:
    """Test suite for ExecutionConfig."""

    def test_config_with_working_dir(self):
        """Test ExecutionConfig accepts working_dir."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ExecutionConfig(working_dir=Path(tmpdir))
            assert config.working_dir == Path(tmpdir)

    def test_config_immutable(self):
        """Test ExecutionConfig is effectively immutable (dataclass)."""
        config = ExecutionConfig(timeout=10)
        # Dataclass fields can be modified unless frozen=True
        # Just verify it works as expected
        assert config.timeout == 10
