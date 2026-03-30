"""Hybrid code generator with fallback hierarchy.

This module provides the HybridCodeGenerator class that combines
template-based and LLM-based generation with automatic fallback.
"""

import re
from typing import Any, Dict, Optional

from src.extraction.schema import Algorithm, Step, StepType
from src.generation.code_generator import GeneratedCode, TemplateCodeGenerator
from src.generation.errors import LLMGenerationError
from src.generation.llm_generator import LLMCodeGenerator


class HybridGenerationResult:
    """
    Result of hybrid code generation with metadata.
    
    Attributes:
        generated: GeneratedCode object
        strategy: Which strategy was used
        fallback_used: Whether fallback was triggered
        steps_generated: Number of steps
    """
    def __init__(self, generated: GeneratedCode, strategy: str,
                 fallback_used: bool = False, steps_generated: int = 0):
        self.generated = generated
        self.strategy = strategy
        self.fallback_used = fallback_used
        self.steps_generated = steps_generated


class HybridCodeGenerator:
    """
    Hybrid generator with Template → LLM → Stub fallback hierarchy.
    
    Automatically selects the best generation strategy based on
    step complexity and availability.
    """
    
    def __init__(self,
                 template_gen: Optional[TemplateCodeGenerator] = None,
                 llm_gen: Optional[LLMCodeGenerator] = None):
        """
        Initialize hybrid generator.
        
        Args:
            template_gen: Optional template generator
            llm_gen: Optional LLM generator
        """
        self.template_gen = template_gen or TemplateCodeGenerator()
        self.llm_gen = llm_gen or LLMCodeGenerator()
        self.used_llm = False
        self.used_template = False
    
    def generate(self, algorithm: Algorithm,
                 strategy: str = "auto") -> GeneratedCode:
        """
        Generate code using hybrid approach.
        
        Args:
            algorithm: Algorithm to generate code for
            strategy: "auto" | "template_only" | "llm_only"
            
        Returns:
            GeneratedCode with source and metadata
        """
        if strategy == "template_only":
            return self._template_generate(algorithm)
        elif strategy == "llm_only":
            return self._llm_generate(algorithm)
        else:  # auto
            return self._hybrid_generate(algorithm)
    
    def _hybrid_generate(self, algorithm: Algorithm) -> GeneratedCode:
        """
        Hybrid generation with automatic fallback.
        
        Flow:
        1. Try template generation for all steps
        2. If any step fails, try LLM for that step
        3. If LLM fails, use stub
        
        Args:
            algorithm: Algorithm to generate code for
            
        Returns:
            GeneratedCode
        """
        # Check if all steps can be handled by templates
        template_compatible = all(
            self._is_template_compatible(step)
            for step in algorithm.steps
        )
        
        if template_compatible:
            self.used_template = True
            return self.template_gen.generate(algorithm)
        
        # Some steps need LLM
        try:
            self.used_llm = True
            return self.llm_gen.generate(algorithm)
        except LLMGenerationError:
            # Fall back to stub
            return self.llm_gen._generate_stub(algorithm)
    
    def _template_generate(self, algorithm: Algorithm) -> GeneratedCode:
        """Generate using template generator only."""
        self.used_template = True
        return self.template_gen.generate(algorithm)
    
    def _llm_generate(self, algorithm: Algorithm) -> GeneratedCode:
        """Generate using LLM generator only."""
        self.used_llm = True
        return self.llm_gen.generate_with_fallback(algorithm)
    
    def _is_template_compatible(self, step: Step) -> bool:
        """
        Check if step can be handled by templates.
        
        Templates handle: ASSIGNMENT, LOOP_FOR, LOOP_WHILE,
        CONDITIONAL, RETURN, CALL, COMMENT
        
        LLM handles: Complex expressions, custom logic
        
        Args:
            step: Step to check
            
        Returns:
            True if template-compatible
        """
        # Check step type
        if step.type not in [
            StepType.ASSIGNMENT,
            StepType.LOOP_FOR,
            StepType.LOOP_WHILE,
            StepType.CONDITIONAL,
            StepType.RETURN,
            StepType.CALL,
            StepType.COMMENT
        ]:
            return False
        
        return self._is_simple_expression(step)
    
    def _is_simple_expression(self, step: Step) -> bool:
        """
        Check if expression is simple enough for templates.
        
        Args:
            step: Step to check
            
        Returns:
            True if expression is simple
        """
        if step.expression:
            # Check for complex patterns
            complex_patterns = [
                r'sum\s+of',      # Summation
                r'product\s+of',  # Product
                r'argmin|argmax', # Optimization
                r'minimum|maximum', # Min/max
                r'forall|exists', # Quantifiers
            ]
            
            for pattern in complex_patterns:
                if re.search(pattern, step.expression, re.IGNORECASE):
                    return False
        
        return True
    
    def get_generation_strategy(self) -> str:
        """Return which strategy was used for last generation."""
        if self.used_template:
            return "template"
        elif self.used_llm:
            return "llm"
        else:
            return "stub"
    
    def generate_for_workflow(self, algorithm: Algorithm) -> Dict[str, Any]:
        """
        Generate code with metadata for workflow.
        
        Args:
            algorithm: Algorithm to generate code for
            
        Returns:
            Dict with:
            - generated: GeneratedCode object
            - strategy: "template" | "llm" | "stub"
            - fallback_used: bool
            - steps_generated: int
        """
        generated = self.generate(algorithm)
        
        return {
            'generated': generated,
            'strategy': self.get_generation_strategy(),
            'fallback_used': self.used_llm and not self.used_template,
            'steps_generated': len(algorithm.steps),
        }


__all__ = [
    "HybridCodeGenerator",
    "HybridGenerationResult",
]
