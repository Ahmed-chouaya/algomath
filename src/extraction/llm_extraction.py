"""LLM-based extraction for algorithms."""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from .schema import Algorithm, Step, StepType
from .parser import RuleBasedParser


@dataclass
class ExtractionResult:
    """Result of algorithm extraction."""
    success: bool
    algorithm: Optional[Algorithm] = None
    method: str = "unknown"
    errors: List[str] = None
    raw_response: Optional[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


def extract_algorithm_llm(
    text: str,
    name: Optional[str] = None,
    model: Optional[str] = None
) -> ExtractionResult:
    """
    Extract algorithm using LLM.
    
    This is a stub implementation. In production, this would call
    an LLM API to extract structured steps from natural language.
    """
    # Fallback to rule-based parser
    parser = RuleBasedParser()
    algorithm = parser.parse(text, name or "unnamed")
    
    return ExtractionResult(
        success=True,
        algorithm=algorithm,
        method="rule_based",
        errors=[]
    )


class HybridExtractor:
    """Hybrid extractor using LLM with rule-based fallback."""

    def __init__(self, model: Optional[str] = None):
        self.model = model
        self.rule_parser = RuleBasedParser()

    def extract(
        self,
        text: str,
        name: Optional[str] = None,
        prefer_llm: bool = True
    ) -> ExtractionResult:
        """
        Extract algorithm using hybrid approach.
        
        Args:
            text: Algorithm text to extract
            name: Optional algorithm name
            prefer_llm: Whether to prefer LLM over rule-based
            
        Returns:
            ExtractionResult with algorithm or errors
        """
        # For now, always use rule-based
        # In production, this would try LLM first, fallback to rule-based
        algorithm = self.rule_parser.parse(text, name or "unnamed")
        
        return ExtractionResult(
            success=True,
            algorithm=algorithm,
            method="rule_based",
            errors=[]
        )

    def extract_with_fallback(
        self,
        text: str,
        name: Optional[str] = None
    ) -> ExtractionResult:
        """Extract with automatic fallback on failure."""
        return self.extract(text, name, prefer_llm=True)
