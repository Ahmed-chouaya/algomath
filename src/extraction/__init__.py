"""Extraction module for AlgoMath.

This module provides algorithm extraction from natural language descriptions,
including rule-based parsing and LLM-based extraction with hybrid fallback.
"""

from .schema import Algorithm, Step, StepType, algorithm_to_json
from .parser import RuleBasedParser
from .prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_PROMPT_TEMPLATE, format_extraction_prompt
from .llm_extraction import HybridExtractor, ExtractionResult, extract_algorithm_llm
from .review import ReviewInterface, validate_step_edit, apply_edits

__all__ = [
    # Schema
    'Algorithm',
    'Step',
    'StepType',
    'algorithm_to_json',
    # Parser
    'RuleBasedParser',
    # Prompts
    'EXTRACTION_SYSTEM_PROMPT',
    'EXTRACTION_USER_PROMPT_TEMPLATE',
    'format_extraction_prompt',
    # LLM Extraction
    'HybridExtractor',
    'ExtractionResult',
    'extract_algorithm_llm',
    # Review
    'ReviewInterface',
    'validate_step_edit',
    'apply_edits',
]
