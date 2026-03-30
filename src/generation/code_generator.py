"""Code generator for algorithms.

This module provides the TemplateCodeGenerator class for
converting structured algorithms into Python code.
"""

import ast
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.extraction.schema import Algorithm, Step, StepType
from src.generation.templates import TemplateRegistry
from src.generation.types import TypeInferrer, ValidationResult, FunctionSignature


@dataclass
class GeneratedCode:
    """
    Represents generated Python code with metadata.
    
    Attributes:
        source: Complete Python source code
        algorithm_name: Name of the source algorithm
        imports: List of required imports
        validation_result: Syntax validation results
    """
    source: str
    algorithm_name: str
    imports: List[str] = field(default_factory=list)
    validation_result: Optional[ValidationResult] = None


class TemplateCodeGenerator:
    """
    Generate Python code from algorithms using templates.
    
    Uses template-based generation for predictable constructs
    like assignments, loops, and conditionals.
    """
    
    def __init__(self, template_registry: Optional[TemplateRegistry] = None):
        """
        Initialize the code generator.
        
        Args:
            template_registry: Optional custom template registry
        """
        self.templates = template_registry or TemplateRegistry()
        self.type_inferrer = TypeInferrer()
        self._step_map: Dict[int, Step] = {}
    
    def generate(self, algorithm: Algorithm) -> GeneratedCode:
        """
        Generate complete Python code from algorithm.
        
        Args:
            algorithm: Algorithm to generate code for
            
        Returns:
            GeneratedCode with source and metadata
        """
        # Build step lookup
        self._step_map = {step.id: step for step in algorithm.steps}
        
        # Generate code sections
        imports = self._generate_imports(algorithm)
        signature = self._generate_signature(algorithm)
        docstring = self._generate_docstring(algorithm)
        body = self._generate_body(algorithm.steps)
        guard = self._generate_execution_guard(algorithm)
        
        # Assemble source
        source_lines = []
        if imports:
            source_lines.append(imports)
            source_lines.append("")
        
        source_lines.append(signature)
        source_lines.append(f'    """{docstring}"""')
        source_lines.append("")
        
        if body:
            source_lines.append(body)
        else:
            source_lines.append("    pass")
        
        source = '\n'.join(source_lines)
        
        # Validate syntax
        validation = self._validate_syntax(source)
        
        # Add execution guard
        if guard:
            source += '\n\n' + guard
        
        # Extract imports
        import_list = self._extract_imports(imports)
        
        return GeneratedCode(
            source=source,
            algorithm_name=algorithm.name,
            imports=import_list,
            validation_result=validation
        )
    
    def _generate_imports(self, algorithm: Algorithm) -> str:
        """
        Generate import section based on detected types.
        
        Args:
            algorithm: Algorithm to analyze
            
        Returns:
            Import statements
        """
        imports = []
        
        # Always include typing
        imports.append("from typing import List, Dict, Optional, Union, Tuple, Any")
        
        # Check if numpy is needed
        for inp in algorithm.inputs:
            name = inp.get("name", "")
            if self.type_inferrer.infer_variable_type(name, inp) == "np.ndarray":
                imports.append("import numpy as np")
                break
        
        # Check if math is needed
        if any("math." in step.description or "sqrt" in step.description 
               for step in algorithm.steps):
            imports.append("import math")
        
        return '\n'.join(imports)
    
    def _generate_signature(self, algorithm: Algorithm) -> str:
        """
        Generate function signature.
        
        Args:
            algorithm: Algorithm to generate signature for
            
        Returns:
            Function definition line
        """
        sig = self.type_inferrer.infer_function_signature(algorithm)
        
        params_str = sig.format_params()
        return f"def {sig.name}({params_str}) -> {sig.return_type}:"
    
    def _generate_docstring(self, algorithm: Algorithm) -> str:
        """
        Generate Google-style docstring.
        
        Args:
            algorithm: Algorithm to generate docstring for
            
        Returns:
            Docstring content
        """
        lines = []
        
        # Summary
        lines.append(algorithm.description or f"{algorithm.name} implementation.")
        lines.append("")
        
        # Args section
        if algorithm.inputs:
            lines.append("Args:")
            for inp in algorithm.inputs:
                name = inp.get("name", "")
                desc = inp.get("description", "")
                ptype = self.type_inferrer.infer_variable_type(name, inp)
                lines.append(f"    {name} ({ptype}): {desc}")
            lines.append("")
        
        # Returns section
        if algorithm.outputs:
            lines.append("Returns:")
            for out in algorithm.outputs:
                name = out.get("name", "")
                desc = out.get("description", "")
                lines.append(f"    {name}: {desc}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_body(self, steps: List[Step], indent: int = 4) -> str:
        """
        Generate function body from steps.
        
        Args:
            steps: Algorithm steps
            indent: Indentation level
            
        Returns:
            Body code string
        """
        lines = []
        
        for step in steps:
            code = self._format_step(step, indent)
            if code:
                lines.append(code)
        
        if not lines:
            return ""
        
        return '\n'.join(lines)
    
    def _format_step(self, step: Step, indent: int = 4) -> str:
        """
        Format a single step into Python code.
        
        Args:
            step: Step to format
            indent: Indentation level
            
        Returns:
            Formatted code
        """
        indent_str = ' ' * indent
        
        if step.type == StepType.ASSIGNMENT:
            target = step.outputs[0] if step.outputs else "result"
            expression = step.expression or "None"
            return f"{indent_str}{target} = {expression}"
        
        elif step.type == StepType.LOOP_FOR:
            iter_var = step.iter_var or "i"
            iter_range = step.iter_range or "range(n)"
            
            lines = [f"{indent_str}for {iter_var} in {iter_range}:"]
            
            # Format body
            body_code = self._format_body(step.body, indent + 4)
            if body_code:
                lines.append(body_code)
            else:
                lines.append(f"{' ' * (indent + 4)}pass")
            
            return '\n'.join(lines)
        
        elif step.type == StepType.LOOP_WHILE:
            condition = step.condition or "True"
            
            lines = [f"{indent_str}while {condition}:"]
            
            body_code = self._format_body(step.body, indent + 4)
            if body_code:
                lines.append(body_code)
            else:
                lines.append(f"{' ' * (indent + 4)}pass")
            
            return '\n'.join(lines)
        
        elif step.type == StepType.CONDITIONAL:
            condition = step.condition or "True"
            
            lines = [f"{indent_str}if {condition}:"]
            
            # Format if body
            if_body = self._format_body(step.body, indent + 4)
            if if_body:
                lines.append(if_body)
            else:
                lines.append(f"{' ' * (indent + 4)}pass")
            
            # Format else body if present
            if step.else_body:
                lines.append(f"{indent_str}else:")
                else_body = self._format_body(step.else_body, indent + 4)
                if else_body:
                    lines.append(else_body)
                else:
                    lines.append(f"{' ' * (indent + 4)}pass")
            
            return '\n'.join(lines)
        
        elif step.type == StepType.RETURN:
            expression = step.expression or "None"
            return f"{indent_str}return {expression}"
        
        elif step.type == StepType.CALL:
            call_target = step.call_target or "function"
            arguments = ", ".join(step.arguments) if step.arguments else ""
            return f"{indent_str}{call_target}({arguments})"
        
        elif step.type == StepType.COMMENT:
            annotation = step.annotation or step.description
            return f"{indent_str}# {annotation}"
        
        return f"{indent_str}# TODO: {step.description}"
    
    def _format_body(self, body_step_ids: List[int], indent: int) -> str:
        """
        Format body steps.
        
        Args:
            body_step_ids: List of step IDs in body
            indent: Indentation level
            
        Returns:
            Formatted body code
        """
        lines = []
        
        for step_id in body_step_ids:
            step = self._step_map.get(step_id)
            if step:
                code = self._format_step(step, indent)
                if code:
                    lines.append(code)
        
        if not lines:
            return ""
        
        return '\n'.join(lines)
    
    def _generate_execution_guard(self, algorithm: Algorithm) -> str:
        """
        Generate execution guard for example usage.
        
        Args:
            algorithm: Algorithm to generate guard for
            
        Returns:
            Execution guard code
        """
        sig = self.type_inferrer.infer_function_signature(algorithm)
        
        lines = [
            'if __name__ == "__main__":',
            '    # Example usage',
            '    pass',
        ]
        
        return '\n'.join(lines)
    
    def _validate_syntax(self, code: str) -> ValidationResult:
        """
        Validate Python syntax using ast module.
        
        Args:
            code: Code to validate
            
        Returns:
            ValidationResult with errors if any
        """
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
    
    def _extract_imports(self, imports_section: str) -> List[str]:
        """Extract module names from imports section."""
        imports = []
        for line in imports_section.split('\n'):
            if line.startswith('import '):
                imports.append(line.replace('import ', ''))
            elif line.startswith('from '):
                parts = line.split()
                if len(parts) >= 2:
                    imports.append(parts[1])
        return imports
