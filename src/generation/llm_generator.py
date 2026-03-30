"""LLM-based code generator.

This module provides the LLMCodeGenerator class for generating
Python code using LLM assistance for complex expressions.
"""

import ast
import re
from typing import Any, Dict, List, Optional

from src.extraction.schema import Algorithm
from src.generation.code_generator import GeneratedCode
from src.generation.errors import LLMGenerationError
from src.generation.prompts import (
    format_code_generation_prompt,
    format_complex_expression_prompt,
)
from src.generation.types import TypeInferrer, ValidationResult


class LLMCodeGenerator:
    """
    Generate code using LLM for complex constructs.
    
    Falls back to template generation when LLM is unavailable
    or for simple constructs.
    """
    
    def __init__(self,
                 model: str = "claude-3-5-haiku",
                 temperature: float = 0.2,
                 timeout: int = 30):
        """
        Initialize the LLM code generator.
        
        Args:
            model: LLM model to use
            temperature: Sampling temperature
            timeout: Request timeout in seconds
        """
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.type_inferrer = TypeInferrer()
    
    def generate(self, algorithm: Algorithm) -> GeneratedCode:
        """
        Generate code using LLM for complex constructs.
        
        Uses hybrid approach:
        - LLM for complex expressions templates can't handle
        - Type inference for type hints
        - AST validation for syntax checking
        
        Args:
            algorithm: Algorithm to generate code for
            
        Returns:
            GeneratedCode with source and metadata
            
        Raises:
            LLMGenerationError: If LLM generation fails
        """
        try:
            # Format prompt for LLM
            messages = format_code_generation_prompt(algorithm)
            
            # Call LLM (simulated - would use actual LLM API)
            code = self._call_llm(messages)
            
            if not code:
                raise LLMGenerationError("LLM returned empty response")
            
            # Validate syntax
            validation = self._validate_syntax(code)
            
            return GeneratedCode(
                source=code,
                algorithm_name=algorithm.name,
                imports=[],
                validation_result=validation
            )
            
        except Exception as e:
            raise LLMGenerationError(f"LLM generation failed: {e}")
    
    def generate_docstring(self, algorithm: Algorithm) -> str:
        """
        Generate comprehensive docstring via LLM.
        
        Args:
            algorithm: Algorithm to generate docstring for
            
        Returns:
            Formatted docstring
        """
        try:
            from src.generation.prompts import format_docstring_generation_prompt
            messages = format_docstring_generation_prompt(algorithm)
            docstring = self._call_llm(messages)
            return docstring or self._fallback_docstring(algorithm)
        except Exception:
            return self._fallback_docstring(algorithm)
    
    def generate_complex_expression(self,
                                    expression: str,
                                    context: Dict[str, Any] = None) -> str:
        """
        Generate Python code for complex mathematical expression.
        
        Args:
            expression: Mathematical expression text
            context: Variable context (available vars, types)
            
        Returns:
            Python code string
        """
        messages = format_complex_expression_prompt(expression, context)
        code = self._call_llm(messages)
        return code or expression
    
    def _call_llm(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Call LLM API with messages.
        
        This is a stub - actual implementation would use
        Anthropic, OpenAI, or other LLM API.
        
        Args:
            messages: List of message dicts
            
        Returns:
            LLM response text or None
        """
        # TODO: Implement actual LLM API call
        # For now, return None to trigger fallback
        return None
    
    def _validate_syntax(self, code: str) -> ValidationResult:
        """Validate Python syntax."""
        try:
            ast.parse(code)
            return ValidationResult(is_valid=True, errors=[], warnings=[])
        except SyntaxError as e:
            return ValidationResult(
                is_valid=False,
                errors=[{
                    'message': f"Syntax error: {e.msg}",
                    'line': e.lineno,
                    'type': 'syntax',
                    'text': e.text
                }],
                warnings=[]
            )
    
    def _fallback_docstring(self, algorithm: Algorithm) -> str:
        """Generate basic docstring when LLM fails."""
        lines = []
        lines.append(algorithm.description or f"{algorithm.name} implementation.")
        lines.append("")
        
        if algorithm.inputs:
            lines.append("Args:")
            for inp in algorithm.inputs:
                name = inp.get('name', '')
                desc = inp.get('description', '')
                ptype = self.type_inferrer.infer_variable_type(name, inp)
                lines.append(f"    {name} ({ptype}): {desc}")
            lines.append("")
        
        if algorithm.outputs:
            lines.append("Returns:")
            for out in algorithm.outputs:
                name = out.get('name', '')
                desc = out.get('description', '')
                lines.append(f"    {name}: {desc}")
        
        return '\n'.join(lines)
    
    def _generate_stub(self, algorithm: Algorithm) -> GeneratedCode:
        """
        Generate stub code when LLM fails.
        
        Args:
            algorithm: Algorithm to generate stub for
            
        Returns:
            GeneratedCode with stub implementation
        """
        sig = self.type_inferrer.infer_function_signature(algorithm)
        
        stub = f'''def {sig.name}({sig.format_params()}) -> {sig.return_type}:
    """Stub implementation - LLM generation failed.
    
    Steps: {[s.description for s in algorithm.steps]}
    """
    raise NotImplementedError("Algorithm not yet implemented")
'''
        
        return GeneratedCode(
            source=stub,
            algorithm_name=algorithm.name,
            imports=[],
            validation_result=ValidationResult(is_valid=True, errors=[], warnings=[])
        )
    
    def generate_with_fallback(self, algorithm: Algorithm) -> GeneratedCode:
        """
        Generate code with graceful fallback.
        
        Args:
            algorithm: Algorithm to generate code for
            
        Returns:
            GeneratedCode (may be stub on failure)
        """
        try:
            return self.generate(algorithm)
        except LLMGenerationError:
            return self._generate_stub(algorithm)


__all__ = ["LLMCodeGenerator"]
