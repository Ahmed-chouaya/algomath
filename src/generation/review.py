"""Code review interface.

This module provides the CodeReviewInterface for reviewing
and editing generated Python code.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.extraction.schema import Algorithm
from src.generation.code_generator import GeneratedCode
from src.generation.validation import CodeValidator, ValidationResult


@dataclass
class ReviewState:
    """
    State of code review.
    
    Attributes:
        original_code: Original generated code
        current_code: Current (possibly edited) code
        is_edited: Whether code has been edited
        is_approved: Whether code is approved
        validation_result: Last validation result
        approved_at: Approval timestamp
    """
    original_code: str
    current_code: str
    is_edited: bool = False
    is_approved: bool = False
    validation_result: Optional[ValidationResult] = None
    approved_at: Optional[datetime] = None


class CodeReviewInterface:
    """
    Review and edit generated Python code.
    
    Provides side-by-side view of steps and code,
    editing capability, and approval workflow.
    """
    
    def __init__(self, validator: Optional[CodeValidator] = None):
        """
        Initialize review interface.
        
        Args:
            validator: Optional custom validator
        """
        self.validator = validator or CodeValidator()
        self.state: Optional[ReviewState] = None
        self.algorithm: Optional[Algorithm] = None
        self.generated: Optional[GeneratedCode] = None
    
    def load(self, algorithm: Algorithm, generated: GeneratedCode):
        """
        Load algorithm and generated code for review.
        
        Args:
            algorithm: Algorithm that was generated from
            generated: Generated code
        """
        self.algorithm = algorithm
        self.generated = generated
        self.state = ReviewState(
            original_code=generated.source,
            current_code=generated.source,
            is_edited=False,
            is_approved=False
        )
    
    def display(self) -> str:
        """
        Display side-by-side view of steps and code.
        
        Returns:
            Formatted display string
        """
        if not self.state:
            return "No code loaded for review."
        
        lines = []
        lines.append("╔════════════════════════════════════════════════════════════╗")
        lines.append("║ Algorithm Steps          │ Generated Code                ║")
        lines.append("╠════════════════════════════════════════════════════════════╣")
        
        # Format steps
        steps_text = self._format_steps()
        code_lines = self.state.current_code.split('\n')
        
        # Side-by-side display
        step_lines = steps_text.split('\n')
        max_lines = max(len(step_lines), len(code_lines))
        
        for i in range(max_lines):
            step_part = step_lines[i] if i < len(step_lines) else ""
            code_part = code_lines[i] if i < len(code_lines) else ""
            
            # Truncate to fit display
            step_part = step_part[:30].ljust(30)
            code_part = code_part[:40]
            
            lines.append(f"║ {step_part} │ {code_part} ║")
        
        lines.append("╚════════════════════════════════════════════════════════════╝")
        
        # Status line
        status = []
        if self.state.is_edited:
            status.append("[EDITED]")
        if self.state.is_approved:
            status.append("[APPROVED]")
        if self.state.validation_result and not self.state.validation_result.is_valid:
            status.append(f"[{self.state.validation_result.error_count} ERRORS]")
        
        lines.append(f"Status: {' '.join(status) if status else 'Ready for review'}")
        
        return '\n'.join(lines)
    
    def _format_steps(self) -> str:
        """Format algorithm steps for display."""
        if not self.algorithm:
            return "No algorithm loaded"
        
        lines = []
        for i, step in enumerate(self.algorithm.steps, 1):
            desc = step.description[:27] + "..." if len(step.description) > 30 else step.description
            lines.append(f"{i}. {desc}")
        return '\n'.join(lines)
    
    def edit_code(self, new_code: str) -> ValidationResult:
        """
        Update code with user edits.
        
        Args:
            new_code: New code from user edits
            
        Returns:
            ValidationResult for the edited code
        """
        if not self.state:
            raise ValueError("No code loaded")
        
        self.state.current_code = new_code
        self.state.is_edited = True
        self.state.is_approved = False  # Reset approval on edit
        
        # Validate edited code
        self.state.validation_result = self.validator.validate(new_code)
        
        return self.state.validation_result
    
    def validate_edit(self) -> ValidationResult:
        """
        Re-validate current code.
        
        Returns:
            ValidationResult
        """
        if not self.state:
            raise ValueError("No code loaded")
        
        self.state.validation_result = self.validator.validate(
            self.state.current_code
        )
        return self.state.validation_result
    
    def approve(self) -> bool:
        """
        Mark code as approved.
        
        Returns:
            True if approved successfully
        """
        if not self.state:
            raise ValueError("No code loaded")
        
        # Must validate first
        if not self.state.validation_result:
            self.validate_edit()
        
        if self.state.validation_result and not self.state.validation_result.is_valid:
            return False  # Cannot approve invalid code
        
        self.state.is_approved = True
        self.state.approved_at = datetime.now()
        return True
    
    def is_approved(self) -> bool:
        """Check if code is approved."""
        return self.state.is_approved if self.state else False
    
    def get_modified_code(self) -> str:
        """Return user-edited code (or original if not edited)."""
        return self.state.current_code if self.state else ""
    
    def get_original_code(self) -> str:
        """Return original generated code."""
        return self.state.original_code if self.state else ""
    
    def has_changes(self) -> bool:
        """Check if code was edited."""
        if not self.state:
            return False
        return self.state.current_code != self.state.original_code
    
    def get_review_summary(self) -> Dict[str, Any]:
        """
        Return summary of review state.
        
        Returns:
            Dict with review state
        """
        if not self.state:
            return {}
        
        return {
            'is_edited': self.state.is_edited,
            'is_approved': self.state.is_approved,
            'has_validation_errors': (
                self.state.validation_result and
                not self.state.validation_result.is_valid
            ) if self.state.validation_result else False,
            'validation_errors': (
                self.state.validation_result.errors
            ) if self.state.validation_result else [],
            'line_count': len(self.state.current_code.split('\n')),
        }


def create_review(algorithm: Algorithm,
                  generated: GeneratedCode) -> CodeReviewInterface:
    """
    Factory function to create review interface.
    
    Args:
        algorithm: Algorithm that was generated from
        generated: Generated code
        
    Returns:
        CodeReviewInterface instance
    """
    review = CodeReviewInterface()
    review.load(algorithm, generated)
    return review


__all__ = [
    'CodeReviewInterface',
    'ReviewState',
    'create_review',
]
