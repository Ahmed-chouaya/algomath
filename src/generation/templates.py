"""Code templates for algorithm generation.

This module provides templates for generating Python code
from structured algorithm steps.
"""

import re
from typing import Dict, Optional

from src.extraction.schema import Step, StepType


class CodeTemplates:
    """Collection of code templates for mathematical operations."""
    
    # Mathematical operator templates
    summation = "sum({expression} for {iter_var} in {iter_range})"
    product = "math.prod([{expression} for {iter_var} in {iter_range}])"
    sqrt = "math.sqrt({expression})"
    abs = "abs({expression})"
    
    # Set operations
    element_in = "{element} in {set_name}"
    subset = "{set_a} <= {set_b}"
    
    # Matrix operations
    matrix_mult = "{matrix_a} @ {matrix_b}"
    matrix_transpose = "{matrix}.T"
    
    # Optimization
    argmin = "np.argmin({array})"
    argmax = "np.argmax({array})"
    minimum = "min({expression})"
    maximum = "max({expression})"


class TemplateRegistry:
    """
    Registry mapping StepType to code templates.
    
    Provides templates for generating Python code from
    structured algorithm steps.
    """
    
    DEFAULT_TEMPLATES: Dict[StepType, str] = {
        StepType.ASSIGNMENT: "{target} = {expression}",
        StepType.LOOP_FOR: "for {iter_var} in {iter_range}:\n{body}",
        StepType.LOOP_WHILE: "while {condition}:\n{body}",
        StepType.CONDITIONAL: "if {condition}:\n{if_body}{else_clause}",
        StepType.RETURN: "return {expression}",
        StepType.CALL: "{call_target}({arguments})",
        StepType.COMMENT: "# {annotation}",
    }
    
    def __init__(self):
        """Initialize template registry with default templates."""
        self._templates = self.DEFAULT_TEMPLATES.copy()
    
    def register(self, step_type: StepType, template: str) -> None:
        """
        Register or override a template for a StepType.
        
        Args:
            step_type: Type of step
            template: Template string with placeholders
        """
        self._templates[step_type] = template
    
    def get(self, step_type: StepType) -> str:
        """
        Get template for a StepType.
        
        Args:
            step_type: Type of step
            
        Returns:
            Template string
        """
        return self._templates.get(step_type, "# TODO: {description}")
    
    def format_step(self, step: Step, indent: int = 4) -> str:
        """
        Format a step using its template.
        
        Args:
            step: Step to format
            indent: Indentation level for nested content
            
        Returns:
            Formatted code string
        """
        template = self.get(step.type)
        
        if step.type == StepType.ASSIGNMENT:
            target = step.outputs[0] if step.outputs else "result"
            expression = step.expression or "None"
            return template.format(target=target, expression=expression)
        
        elif step.type == StepType.LOOP_FOR:
            iter_var = step.iter_var or "i"
            iter_range = step.iter_range or "range(n)"
            body = self._format_body(step.body, indent + 4)
            code = template.format(
                iter_var=iter_var,
                iter_range=iter_range,
                body=body
            )
            return self.indent_lines(code, indent)
        
        elif step.type == StepType.LOOP_WHILE:
            condition = step.condition or "True"
            body = self._format_body(step.body, indent + 4)
            code = template.format(condition=condition, body=body)
            return self.indent_lines(code, indent)
        
        elif step.type == StepType.CONDITIONAL:
            condition = step.condition or "True"
            if_body = self._format_body(step.body, indent + 4)
            
            if step.else_body:
                else_body = self._format_body(step.else_body, indent + 4)
                else_clause = f"\nelse:\n{else_body}"
            else:
                else_clause = ""
            
            code = template.format(
                condition=condition,
                if_body=if_body,
                else_clause=else_clause
            )
            return self.indent_lines(code, indent)
        
        elif step.type == StepType.RETURN:
            expression = step.expression or "None"
            return template.format(expression=expression)
        
        elif step.type == StepType.CALL:
            call_target = step.call_target or "function"
            arguments = ", ".join(step.arguments) if step.arguments else ""
            return template.format(call_target=call_target, arguments=arguments)
        
        elif step.type == StepType.COMMENT:
            annotation = step.annotation or step.description
            return template.format(annotation=annotation)
        
        return template.format(description=step.description)
    
    def _format_body(self, body_step_ids: list, indent: int) -> str:
        """
        Format body steps (placeholder - actual implementation needs step lookup).
        
        Args:
            body_step_ids: List of step IDs in body
            indent: Indentation level
            
        Returns:
            Formatted body code
        """
        if not body_step_ids:
            return self.indent_lines("pass", indent)
        # This would require access to the step map
        # For now, return pass
        return self.indent_lines("# body steps would go here", indent)
    
    def indent_lines(self, code: str, level: int) -> str:
        """
        Indent multi-line code.
        
        Args:
            code: Code string
            level: Indentation level (spaces)
            
        Returns:
            Indented code
        """
        if not code:
            return ""
        
        lines = code.split('\n')
        indent = ' ' * level
        return '\n'.join(indent + line for line in lines)
    
    def format_math_expression(self, expression: str) -> str:
        """
        Format mathematical expression into Python code.
        
        Args:
            expression: Mathematical expression text
            
        Returns:
            Python code string
        """
        result = expression
        
        # Common patterns
        patterns = [
            (r'sum\s+of\s+(.+?)\s+for\s+(\w+)\s+in\s+(.+)', 
             r'sum(\1 for \2 in \3)'),
            (r'product\s+of\s+(.+?)\s+for\s+(\w+)\s+in\s+(.+)', 
             r'math.prod([\1 for \2 in \3])'),
            (r'sqrt\s*\((.+?)\)', r'math.sqrt(\1)'),
            (r'\|(.+?)\|', r'abs(\1)'),
        ]
        
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
