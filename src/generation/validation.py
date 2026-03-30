"""Code validation utilities.

This module provides validation for generated Python code.
"""

import ast
import importlib.util
import re
import subprocess
import tempfile
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.generation.errors import GenerationError, SyntaxGenerationError


@dataclass
class ValidationResult:
    """
    Represents validation results.
    
    Attributes:
        is_valid: Whether validation passed
        errors: List of error dictionaries
        warnings: List of warning messages
    """
    is_valid: bool
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    @property
    def error_count(self) -> int:
        return len(self.errors)


class CodeValidator:
    """
    Validate generated Python code.
    
    Provides syntax, import, and optional runtime validation.
    """
    
    def __init__(self, check_runtime: bool = False):
        """
        Initialize validator.
        
        Args:
            check_runtime: Whether to run runtime checks
        """
        self.check_runtime = check_runtime
        self.errors = []
    
    def validate(self, code: str) -> ValidationResult:
        """
        Run all validation checks.
        
        Args:
            code: Python code to validate
            
        Returns:
            ValidationResult with errors and warnings
        """
        results = []
        
        # Syntax validation
        results.append(self.validate_syntax(code))
        
        # Import validation
        results.append(self.validate_imports(code))
        
        # Runtime check if enabled
        if self.check_runtime:
            results.append(self.validate_runtime(code))
        
        # Merge results
        all_errors = []
        all_warnings = []
        for r in results:
            all_errors.extend(r.errors)
            all_warnings.extend(r.warnings)
        
        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings
        )
    
    def validate_syntax(self, code: str) -> ValidationResult:
        """
        Validate Python syntax using ast module.
        
        Args:
            code: Python code to validate
            
        Returns:
            ValidationResult
        """
        try:
            ast.parse(code)
            return ValidationResult(is_valid=True, errors=[], warnings=[])
        except SyntaxError as e:
            error = {
                'message': f"Syntax error: {e.msg}",
                'line': e.lineno,
                'type': 'syntax',
                'text': e.text
            }
            return ValidationResult(
                is_valid=False,
                errors=[error],
                warnings=[]
            )
    
    def validate_imports(self, code: str) -> ValidationResult:
        """
        Verify imports can be resolved.
        
        Args:
            code: Python code to validate
            
        Returns:
            ValidationResult
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return ValidationResult(is_valid=False, errors=[], warnings=[])
        
        errors = []
        warnings = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if not self._can_import(alias.name.split('.')[0]):
                        errors.append({
                            'message': f"Cannot import module: {alias.name}",
                            'line': node.lineno,
                            'type': 'import'
                        })
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    if not self._can_import(node.module.split('.')[0]):
                        errors.append({
                            'message': f"Cannot import module: {node.module}",
                            'line': node.lineno,
                            'type': 'import'
                        })
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _can_import(self, module_name: str) -> bool:
        """
        Check if module can be imported.
        
        Args:
            module_name: Module name to check
            
        Returns:
            True if module can be imported
        """
        # Built-in modules that don't need checking
        built_ins = {'builtins', 'types', 'typing', 'abc', 'collections'}
        if module_name in built_ins:
            return True
        
        try:
            return importlib.util.find_spec(module_name) is not None
        except (ImportError, ModuleNotFoundError):
            return False
    
    def validate_runtime(self, code: str, timeout: int = 5) -> ValidationResult:
        """
        Execute code in sandbox to check for NameError.
        
        Args:
            code: Python code to validate
            timeout: Timeout in seconds
            
        Returns:
            ValidationResult
        """
        # Create temp file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            # Run with timeout
            result = subprocess.run(
                ['python', temp_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            errors = []
            if result.returncode != 0:
                if 'NameError' in result.stderr:
                    errors.append({
                        'message': f"NameError: {result.stderr}",
                        'line': self._extract_line_from_traceback(result.stderr),
                        'type': 'runtime'
                    })
                elif 'SyntaxError' not in result.stderr:
                    errors.append({
                        'message': f"Runtime error: {result.stderr}",
                        'line': None,
                        'type': 'runtime'
                    })
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=[]
            )
            
        except subprocess.TimeoutExpired:
            return ValidationResult(
                is_valid=False,
                errors=[{
                    'message': f'Runtime validation timed out after {timeout}s',
                    'line': None,
                    'type': 'timeout'
                }],
                warnings=[]
            )
        finally:
            os.unlink(temp_path)
    
    def _extract_line_from_traceback(self, stderr: str) -> Optional[int]:
        """
        Extract line number from traceback.
        
        Args:
            stderr: Stderr text from subprocess
            
        Returns:
            Line number or None
        """
        match = re.search(r'line (\d+)', stderr)
        if match:
            return int(match.group(1))
        return None


def validate_generated(generated_code: Any) -> ValidationResult:
    """
    Validate a GeneratedCode object.
    
    Args:
        generated_code: GeneratedCode object to validate
        
    Returns:
        ValidationResult
    """
    validator = CodeValidator()
    return validator.validate(generated_code.source)


__all__ = [
    'ValidationResult',
    'CodeValidator',
    'validate_generated',
]
