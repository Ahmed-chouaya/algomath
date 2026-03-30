"""Type inference utilities for code generation.

This module provides type inference for mathematical variables
and function signatures based on variable naming conventions.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import re

from src.extraction.schema import Algorithm, Step


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
    errors: List[Dict[str, Any]]
    warnings: List[str]
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    @property
    def error_count(self) -> int:
        return len(self.errors)


@dataclass
class PythonType:
    """Represents a Python type annotation."""
    name: str
    is_optional: bool = False
    
    def __str__(self) -> str:
        if self.is_optional:
            return f"Optional[{self.name}]"
        return self.name


@dataclass
class FunctionSignature:
    """Represents a function signature with parameters and return type."""
    name: str
    params: List[Tuple[str, str]]  # (param_name, type_annotation)
    return_type: str
    
    def format_params(self) -> str:
        """Format parameters for function definition."""
        if not self.params:
            return ""
        return ", ".join(f"{name}: {ptype}" for name, ptype in self.params)


class TypeInferrer:
    """
    Infer Python types from variable names and context.
    
    Uses naming conventions common in mathematical algorithms
    to infer appropriate Python type annotations.
    """
    
    # Variable name patterns → types
    TYPE_PATTERNS = {
        # Integer types
        "int": [
            r'^n$', r'^m$', r'^i$', r'^j$', r'^k$',
            r'count', r'index', r'idx', r'size', r'length',
            r'num', r'number', r'total', r'sum',
        ],
        # Float types
        "float": [
            r'epsilon', r'delta', r'tolerance', r'threshold',
            r'error', r'precision', r'accuracy',
        ],
        # numpy ndarray types
        "np.ndarray": [
            r'matrix', r'^A$', r'^B$', r'^C$', r'^M$',
            r'grid', r'vector', r'^vec', r'^arr',
            r'tensor', r'^T$',
        ],
        # List types
        "List": [
            r'items', r'nodes', r'edges', r'vertices',
            r'elements', r'values', r'keys', r'points',
            r'neighbors', r'adj', r'list',
        ],
        # Dict types
        "Dict": [
            r'dict', r'map', r'hash', r'table',
            r'graph', r'cache', r'memo',
        ],
        # Boolean types
        "bool": [
            r'visited', r'found', r'is_', r'has_',
            r'valid', r'enabled', r'done',
        ],
    }
    
    def infer_variable_type(self, name: str, context: Dict[str, Any]) -> str:
        """
        Infer Python type from variable name.
        
        Args:
            name: Variable name
            context: Additional context (e.g., step information)
            
        Returns:
            Python type annotation string
        """
        name_lower = name.lower()
        
        # Check each type pattern
        for ptype, patterns in self.TYPE_PATTERNS.items():
            for pattern in patterns:
                try:
                    if re.search(pattern, name_lower, re.IGNORECASE):
                        return ptype
                except re.error:
                    # Skip invalid regex patterns
                    continue
        
        # Default to Any for unknown types
        return "Any"
    
    def infer_function_signature(self, algorithm: Algorithm) -> FunctionSignature:
        """
        Infer complete function signature from algorithm.
        
        Args:
            algorithm: Algorithm to infer signature for
            
        Returns:
            FunctionSignature with parameters and return type
        """
        # Infer parameter types from inputs
        params = []
        for inp in algorithm.inputs:
            name = inp.get("name", "")
            inferred_type = self.infer_variable_type(name, inp)
            params.append((name, inferred_type))
        
        # Infer return type from outputs
        if not algorithm.outputs:
            return_type = "None"
        elif len(algorithm.outputs) == 1:
            name = algorithm.outputs[0].get("name", "")
            # Special handling for common output names
            if name.lower() in ["result", "path", "distances", "output", "answer"]:
                return_type = "List[float]"
            else:
                return_type = self.infer_variable_type(name, algorithm.outputs[0])
        else:
            # Multiple outputs → Tuple
            types = []
            for out in algorithm.outputs:
                name = out.get("name", "")
                types.append(self.infer_variable_type(name, out))
            return_type = f"Tuple[{', '.join(types)}]"
        
        return FunctionSignature(
            name=self._to_snake_case(algorithm.name),
            params=params,
            return_type=return_type
        )
    
    def format_type_hint(self, type_str: str, optional: bool = False) -> str:
        """
        Format type hint for PEP 484 compliance.
        
        Args:
            type_str: Type string
            optional: Whether type is optional
            
        Returns:
            Formatted type hint
        """
        if optional and not type_str.startswith("Optional["):
            return f"Optional[{type_str}]"
        return type_str
    
    def _to_snake_case(self, name: str) -> str:
        """Convert algorithm name to snake_case."""
        # Replace spaces and dashes with underscores
        name = re.sub(r'[\s\-]+', '_', name)
        # Insert underscore before uppercase letters
        name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
        return name.lower().strip('_')
