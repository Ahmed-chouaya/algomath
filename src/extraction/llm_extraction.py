"""LLM-based extraction with hybrid fallback to rule-based parser."""

import json
import re
from typing import Optional, List, Any
from dataclasses import dataclass

from .schema import Algorithm, Step, StepType
from .parser import RuleBasedParser
from .prompts import EXTRACTION_SYSTEM_PROMPT, format_extraction_prompt


@dataclass
class ExtractionResult:
    """Result of extraction with metadata."""
    algorithm: Algorithm
    success: bool
    method: str  # "llm" or "rule_based"
    errors: List[str]
    line_references: List[List[int]]

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


def extract_algorithm_llm(
    text: str,
    timeout: int = 30
) -> ExtractionResult:
    """
    Extract algorithm using LLM with rule-based fallback.

    Args:
        text: Algorithm description text
        timeout: Maximum time in seconds (per D-27)

    Returns:
        ExtractionResult with algorithm and metadata

    Per D-01, D-04 from 02-CONTEXT.md.
    """
    errors = []

    try:
        # Format prompt with line numbers
        user_prompt = format_extraction_prompt(text)

        # Call LLM (using agent's completion capability)
        llm_response = _call_llm(
            system=EXTRACTION_SYSTEM_PROMPT,
            user=user_prompt,
            timeout=timeout
        )

        if llm_response:
            # Parse JSON response
            algorithm = _parse_llm_response(llm_response, text)
            if algorithm:
                return ExtractionResult(
                    algorithm=algorithm,
                    success=True,
                    method="llm",
                    errors=[],
                    line_references=[step.line_refs for step in algorithm.steps]
                )

        errors.append("LLM extraction returned no valid result")

    except Exception as e:
        errors.append(f"LLM extraction failed: {str(e)}")

    # Fallback to rule-based parser
    try:
        parser = RuleBasedParser()
        algorithm = parser.parse(text)

        return ExtractionResult(
            algorithm=algorithm,
            success=True,
            method="rule_based",
            errors=errors + ["Fell back to rule-based parser"],
            line_references=[step.line_refs for step in algorithm.steps]
        )

    except Exception as e:
        errors.append(f"Rule-based fallback failed: {str(e)}")

    # Return empty algorithm
    return ExtractionResult(
        algorithm=Algorithm(name="unnamed", source_text=text),
        success=False,
        method="failed",
        errors=errors,
        line_references=[]
    )


def _call_llm(system: str, user: str, timeout: int) -> Optional[str]:
    """
    Call LLM for extraction. Uses agent's native capabilities.

    In actual implementation, this would call the AI assistant.
    For now, returns None to trigger fallback.
    """
    # Placeholder - actual implementation would use agent
    return None


def _parse_llm_response(response: str, original_text: str) -> Optional[Algorithm]:
    """
    Parse LLM JSON response into Algorithm object.

    Args:
        response: JSON string from LLM
        original_text: Original algorithm text

    Returns:
        Algorithm object or None if parsing fails
    """
    try:
        # Extract JSON from response (in case of markdown code blocks)
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response

        # Clean up
        json_str = json_str.strip()

        # Parse JSON
        data = json.loads(json_str)

        # Build Algorithm
        algorithm = Algorithm(
            name=data.get("name", "unnamed"),
            description=data.get("description", ""),
            source_text=original_text
        )

        # Parse inputs
        algorithm.inputs = data.get("inputs", [])

        # Parse outputs
        algorithm.outputs = data.get("outputs", [])

        # Parse steps
        steps = []
        for step_data in data.get("steps", []):
            step_type_str = step_data.get("type", "comment")
            try:
                step_type = StepType(step_type_str)
            except ValueError:
                step_type = StepType.COMMENT

            step = Step(
                id=step_data.get("id", len(steps) + 1),
                type=step_type,
                description=step_data.get("description", ""),
                inputs=step_data.get("inputs", []),
                outputs=step_data.get("outputs", []),
                line_refs=step_data.get("line_refs", []),
                condition=step_data.get("condition"),
                body=step_data.get("body", []),
                else_body=step_data.get("else_body", []),
                iter_var=step_data.get("iter_var"),
                iter_range=step_data.get("iter_range"),
                expression=step_data.get("expression"),
                call_target=step_data.get("call_target"),
                arguments=step_data.get("arguments", []),
                annotation=step_data.get("annotation")
            )
            steps.append(step)

        algorithm.steps = steps

        return algorithm

    except Exception:
        return None


class HybridExtractor:
    """
    Hybrid extractor combining rule-based and LLM extraction.

    Per D-01, D-02 from 02-CONTEXT.md.
    """

    def __init__(self):
        self.rule_parser = RuleBasedParser()
        self.use_llm = True

    def extract(self, text: str, prefer_llm: bool = True) -> ExtractionResult:
        """
        Extract algorithm using preferred method.

        Args:
            text: Algorithm description
            prefer_llm: If True, try LLM first; else use rule-based

        Returns:
            ExtractionResult with extracted algorithm
        """
        if prefer_llm and self.use_llm:
            return extract_algorithm_llm(text)
        else:
            try:
                algorithm = self.rule_parser.parse(text)
                return ExtractionResult(
                    algorithm=algorithm,
                    success=True,
                    method="rule_based",
                    errors=[],
                    line_references=[step.line_refs for step in algorithm.steps]
                )
            except Exception as e:
                return ExtractionResult(
                    algorithm=Algorithm(name="unnamed", source_text=text),
                    success=False,
                    method="failed",
                    errors=[str(e)],
                    line_references=[]
                )
