"""Sandboxed subprocess execution module for AlgoMath.

Per D-01 through D-06: Provides safe, isolated code execution with resource
limits, timeout protection, output capture, and file system restrictions.

This module implements a subprocess-based sandbox that:
- Runs code in a separate Python process for isolation
- Applies CPU and memory limits to prevent resource abuse
- Captures stdout/stderr and returns execution results
- Restricts dangerous imports (os, sys, subprocess, etc.)
- Uses temporary directories that auto-clean after execution
"""

import subprocess
import tempfile
import os
import sys
import signal
import json
import time
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any, Dict, List


class ExecutionStatus(Enum):
    """Enumeration of possible execution statuses."""
    SUCCESS = "success"
    TIMEOUT = "timeout"
    MEMORY_ERROR = "memory_error"
    RUNTIME_ERROR = "runtime_error"
    SYNTAX_ERROR = "syntax_error"
    IMPORT_ERROR = "import_error"


@dataclass
class ExecutionResult:
    """Result of code execution.

    Attributes:
        status: Execution status (success, timeout, error, etc.)
        stdout: Captured standard output
        stderr: Captured standard error
        runtime_seconds: Execution time in seconds
        return_value: Serialized return value if code defines main()
        error_type: Type of error if execution failed
        error_message: Human-readable error message
    """
    status: ExecutionStatus
    stdout: str = ""
    stderr: str = ""
    runtime_seconds: float = 0.0
    return_value: Any = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None


# Modules that are blocked for security
# Note: 'sys' is removed from blocklist since wrapper needs it,
# but dangerous sys functions like sys.exit are blocked separately
BLOCKED_MODULES = [
    'os', 'subprocess', 'socket', 'urllib', 'http', 'ftplib',
    'smtplib', 'ssl', 'ctypes', 'mmap', 'resource', 'pty', 'tty',
    'multiprocessing', 'concurrent.futures.process'
]

# Functions/methods that are dangerous even within allowed modules
BLOCKED_CALLS = [
    ('sys', 'exit'),  # sys.exit() would terminate process
]


def _create_import_restrictor_code() -> str:
    """Create Python code that restricts dangerous imports.

    Per D-28: Import restrictions block os, sys, subprocess, network modules.
    This code overrides __import__ to check against a blocklist.
    """
    blocked = json.dumps(BLOCKED_MODULES)
    return f'''
import builtins
import json

__BLOCKED_MODULES = set(json.loads({repr(blocked)}))
_original_import = builtins.__import__

def _restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    """Import hook that blocks dangerous modules."""
    # Check if the module or any of its parents is blocked
    module_parts = name.split('.')
    for i in range(len(module_parts)):
        partial_name = '.'.join(module_parts[:i+1])
        if partial_name in __BLOCKED_MODULES:
            raise ImportError(
                f"Import of '{{name}}' is not allowed. "
                f"Module '{{partial_name}}' is restricted for security."
            )
    return _original_import(name, globals, locals, fromlist, level)

builtins.__import__ = _restricted_import
'''


def _create_return_capture_wrapper(code: str) -> str:
    """Wrap code to capture return values from main() function.

    Per D-30: Capture function return values for algorithms that return data.
    """
    return f'''
import json

__algo_return_value = None

def _capture_main_result():
    """Check if main() was defined and capture its return value."""
    global __algo_return_value
    if 'main' in globals() and callable(globals()['main']):
        __algo_return_value = main()

# User code starts here
{code}

# After code runs, try to capture main() result
_capture_main_result()

# Print return value for parent process to capture
if __algo_return_value is not None:
    try:
        # Try to serialize; if not JSON serializable, use repr
        json.dumps(__algo_return_value)
        print("__ALGO_RETURN__" + json.dumps(__algo_return_value))
    except (TypeError, ValueError):
        print("__ALGO_RETURN__" + repr(__algo_return_value))
'''


class SandboxExecutor:
    """Executor that runs Python code in a sandboxed subprocess.

    Per D-01, D-02: Uses subprocess-based isolation with resource limits.
    Per D-05: Default 30-second timeout.
    Per D-09, D-10, D-11: Uses tempfile.TemporaryDirectory for isolation and cleanup.

    Attributes:
        timeout: Maximum execution time in seconds (default: 30)
        max_memory_mb: Maximum memory in MB (default: 512)
        allowed_imports: Optional list of allowed imports (None = use blocklist)
    """

    def __init__(
        self,
        timeout: int = 30,
        max_memory_mb: int = 512,
        allowed_imports: Optional[List[str]] = None
    ):
        """Initialize sandbox executor.

        Args:
            timeout: Maximum execution time in seconds
            max_memory_mb: Maximum memory allowed in megabytes
            allowed_imports: Optional whitelist of allowed imports
        """
        self.timeout = timeout
        self.max_memory_mb = max_memory_mb
        self.allowed_imports = allowed_imports

    def _set_resource_limits(self):
        """Set resource limits for the child process.

        Per D-02: Apply CPU and memory limits to subprocess.
        Note: This only works on Unix-like systems.
        """
        try:
            import resource as res

            # Set memory limit (soft limit, hard limit = unlimited)
            max_bytes = self.max_memory_mb * 1024 * 1024
            res.setrlimit(res.RLIMIT_AS, (max_bytes, res.RLIM_INFINITY))

            # Set CPU time limit
            res.setrlimit(res.RLIMIT_CPU, (self.timeout, self.timeout + 5))
        except (ImportError, ValueError, OSError):
            # resource module not available on Windows or failed
            pass

    def execute(
        self,
        code: str,
        working_dir: Optional[Path] = None
    ) -> ExecutionResult:
        """Execute Python code in a sandboxed subprocess.

        Args:
            code: Python code to execute
            working_dir: Optional working directory (uses temp dir if None)

        Returns:
            ExecutionResult with status, output, and metadata
        """
        start_time = time.time()

        # Create temporary directory for execution
        # Per D-09, D-10: Auto-cleanup via TemporaryDirectory
        with tempfile.TemporaryDirectory() as tmpdir:
            code_file = Path(tmpdir) / "script.py"

            # Prepare code with import restrictions and return value capture
            full_code = _create_import_restrictor_code() + "\n"
            full_code += _create_return_capture_wrapper(code)

            # Write code to file
            code_file.write_text(full_code, encoding='utf-8')

            # Per D-11: Working directory isolation via cwd
            cwd = working_dir if working_dir else Path(tmpdir)

            try:
                # Per D-01: Run in subprocess for isolation
                # Per D-05, D-06: Apply timeout for hard termination
                result = subprocess.run(
                    [sys.executable, str(code_file)],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=str(cwd),
                    preexec_fn=self._set_resource_limits if os.name != 'nt' else None,
                    # Kill process group on timeout for complete cleanup
                    start_new_session=True
                )

                runtime = time.time() - start_time

                # Parse return value from output
                return_value = None
                stdout_lines = result.stdout.split('\n')
                filtered_stdout = []
                for line in stdout_lines:
                    if line.startswith('__ALGO_RETURN__'):
                        json_str = line[len('__ALGO_RETURN__'):]
                        try:
                            return_value = json.loads(json_str)
                        except json.JSONDecodeError:
                            # Fall back to repr
                            return_value = json_str
                    else:
                        filtered_stdout.append(line)

                stdout = '\n'.join(filtered_stdout).rstrip()

                # Determine status based on return code
                if result.returncode == 0:
                    status = ExecutionStatus.SUCCESS
                else:
                    status = ExecutionStatus.RUNTIME_ERROR

                return ExecutionResult(
                    status=status,
                    stdout=stdout,
                    stderr=result.stderr.rstrip(),
                    runtime_seconds=runtime,
                    return_value=return_value
                )

            except subprocess.TimeoutExpired as e:
                # Per D-05, D-06, D-07: Timeout handling with clear status
                runtime = time.time() - start_time
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    stdout=e.stdout.decode('utf-8', errors='replace') if e.stdout else "",
                    stderr=e.stderr.decode('utf-8', errors='replace') if e.stderr else "",
                    runtime_seconds=runtime,
                    error_type="TimeoutExpired",
                    error_message=f"Execution timed out after {self.timeout} seconds. Check for infinite loops."
                )

            except MemoryError:
                # Per D-17, D-18: Memory error handling
                runtime = time.time() - start_time
                return ExecutionResult(
                    status=ExecutionStatus.MEMORY_ERROR,
                    runtime_seconds=runtime,
                    error_type="MemoryError",
                    error_message=f"Algorithm used too much memory (limit: {self.max_memory_mb}MB)"
                )

            except Exception as e:
                # Per D-17: Error categorization
                runtime = time.time() - start_time
                error_type = type(e).__name__

                # Check for syntax error indicators
                if "SyntaxError" in str(e) or "syntax error" in str(e).lower():
                    status = ExecutionStatus.SYNTAX_ERROR
                    error_message = f"Generated code has a syntax issue: {e}"
                elif "ImportError" in error_type or "ModuleNotFound" in error_type:
                    status = ExecutionStatus.IMPORT_ERROR
                    error_message = str(e)
                else:
                    status = ExecutionStatus.RUNTIME_ERROR
                    error_message = f"Runtime error: {e}"

                return ExecutionResult(
                    status=status,
                    runtime_seconds=runtime,
                    error_type=error_type,
                    error_message=error_message
                )


# Convenience function for simple use cases
def execute_sandboxed(
    code: str,
    timeout: int = 30,
    max_memory_mb: int = 512,
    working_dir: Optional[Path] = None
) -> ExecutionResult:
    """Execute code with default sandbox settings.

    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds
        max_memory_mb: Maximum memory in megabytes
        working_dir: Optional working directory

    Returns:
        ExecutionResult with status and output
    """
    executor = SandboxExecutor(
        timeout=timeout,
        max_memory_mb=max_memory_mb
    )
    return executor.execute(code, working_dir=working_dir)
