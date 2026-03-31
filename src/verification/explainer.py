"""Algorithm explainer module for AlgoMath.

Provides natural language explanation of algorithm behavior based on
extracted algorithm structures and execution traces.

Per D-05 through D-08: Brief summaries, detailed walkthroughs, execution values,
and complexity-based explanation styles.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import json

from src.extraction.schema import Algorithm, Step, StepType


class ExplanationLevel(Enum):
    """Level of detail for algorithm explanations."""
    BRIEF = "brief"
    DETAILED = "detailed"


@dataclass
class StepExplanation:
    """Explanation of a single step with execution context.

    Per D-07: Shows actual values from execution trace.
    Per D-142: Preserves mathematical notation.
    """
    step_id: int
    description: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    mathematical_notation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "step_id": self.step_id,
            "description": self.description,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "mathematical_notation": self.mathematical_notation,
        }


@dataclass
class ExplanationResult:
    """Result of algorithm explanation.

    Per D-05: Brief summary (1-2 sentences).
    Per D-06: Detailed step-by-step walkthrough.
    Per D-07: Execution trace integration.
    Per D-08: Complexity score for recommendation.
    """
    summary: str
    detailed_explanation: Optional[str] = None
    step_explanations: List[StepExplanation] = field(default_factory=list)
    complexity_score: float = 0.0
    recommended_level: ExplanationLevel = ExplanationLevel.BRIEF
    execution_trace: Optional[Dict[int, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "summary": self.summary,
            "detailed_explanation": self.detailed_explanation,
            "step_explanations": [se.to_dict() for se in self.step_explanations],
            "complexity_score": self.complexity_score,
            "recommended_level": self.recommended_level.value,
            "execution_trace": self.execution_trace,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class AlgorithmExplainer:
    """Explains algorithm behavior in natural language.

    Per D-05: Provides brief summaries.
    Per D-06: Provides detailed step-by-step walkthroughs.
    Per D-07: Shows actual execution values.
    Per D-08: Adapts explanation style to complexity.
    """

    def __init__(self, algorithm: Algorithm):
        """Initialize explainer with algorithm.

        Args:
            algorithm: Algorithm to explain
        """
        self.algorithm = algorithm

    def explain(
        self,
        level: ExplanationLevel = ExplanationLevel.BRIEF,
        execution_trace: Optional[Dict[int, Any]] = None
    ) -> ExplanationResult:
        """Generate explanation of the algorithm.

        Args:
            level: Level of detail (brief or detailed)
            execution_trace: Optional execution values per step

        Returns:
            ExplanationResult with summary and details
        """
        complexity = self._calculate_complexity()
        recommended = self._recommend_level(complexity)

        # Generate summary (always included)
        summary = self._generate_summary()

        # Generate detailed explanation if requested or recommended
        detailed = None
        step_explanations = []
        if level == ExplanationLevel.DETAILED or complexity > 0.5:
            detailed = self._generate_detailed(execution_trace)
            step_explanations = self._generate_step_explanations(execution_trace)

        return ExplanationResult(
            summary=summary,
            detailed_explanation=detailed,
            step_explanations=step_explanations,
            complexity_score=complexity,
            recommended_level=recommended,
            execution_trace=execution_trace
        )

    def explain_step(self, step_id: int) -> StepExplanation:
        """Explain a specific step.

        Args:
            step_id: ID of the step to explain

        Returns:
            StepExplanation with description and details
        """
        step = self._get_step_by_id(step_id)
        if not step:
            return StepExplanation(
                step_id=step_id,
                description=f"Step {step_id} not found"
            )

        description = self._explain_step_by_type(step)
        notation = self._extract_mathematical_notation(step)

        return StepExplanation(
            step_id=step_id,
            description=description,
            inputs={name: None for name in step.inputs},
            outputs={name: None for name in step.outputs},
            mathematical_notation=notation
        )

    def _calculate_complexity(self) -> float:
        """Calculate algorithm complexity score (0.0 to 1.0).

        Per D-08: Simple (<5 steps, no loops) → low score
                  Moderate (5-15 steps, simple loops) → medium
                  Complex (>15 steps, nested loops) → high
        """
        score = 0.0
        num_steps = len(self.algorithm.steps)

        # Step count contribution
        if num_steps < 5:
            score += 0.1
        elif num_steps < 15:
            score += 0.3
        else:
            score += 0.5

        # Check for loops and conditionals
        has_loops = False
        has_conditionals = False
        has_nested = False
        loop_depths = {}

        for step in self.algorithm.steps:
            if step.type in (StepType.LOOP_FOR, StepType.LOOP_WHILE):
                has_loops = True
                loop_depths[step.id] = self._get_loop_depth(step)
                if loop_depths[step.id] > 1:
                    has_nested = True
            elif step.type == StepType.CONDITIONAL:
                has_conditionals = True

        if has_loops:
            score += 0.2
        if has_conditionals:
            score += 0.1
        if has_nested:
            score += 0.2

        return min(score, 1.0)

    def _get_loop_depth(self, step: Step, depth: int = 1) -> int:
        """Calculate nesting depth of a loop."""
        max_depth = depth
        for body_step_id in step.body:
            body_step = self._get_step_by_id(body_step_id)
            if body_step and body_step.type in (StepType.LOOP_FOR, StepType.LOOP_WHILE):
                nested_depth = self._get_loop_depth(body_step, depth + 1)
                max_depth = max(max_depth, nested_depth)
        return max_depth

    def _recommend_level(self, complexity: float) -> ExplanationLevel:
        """Recommend explanation level based on complexity."""
        if complexity < 0.3:
            return ExplanationLevel.BRIEF
        return ExplanationLevel.DETAILED

    def _generate_summary(self) -> str:
        """Generate brief summary (1-2 sentences) per D-05."""
        name = self.algorithm.name
        description = self.algorithm.description
        num_steps = len(self.algorithm.steps)
        num_inputs = len(self.algorithm.inputs)
        num_outputs = len(self.algorithm.outputs)

        # Build input description
        input_desc = ""
        if num_inputs == 1:
            input_name = self.algorithm.inputs[0].get("name", "input")
            input_desc = f"a single {self.algorithm.inputs[0].get('type', 'value')} input {input_name}"
        elif num_inputs > 1:
            input_desc = f"{num_inputs} inputs"
        else:
            input_desc = "no inputs"

        # Build output description
        output_desc = ""
        if num_outputs == 1:
            output_name = self.algorithm.outputs[0].get("name", "result")
            output_desc = f"the {output_name}"
        elif num_outputs > 1:
            output_desc = f"{num_outputs} values"
        else:
            output_desc = "a result"

        # Generate summary sentence
        parts = []
        if description:
            parts.append(f"This {name} algorithm {description.lower()}.")
        else:
            parts.append(f"This is the {name} algorithm.")

        # Add complexity/structure info
        if num_steps < 5:
            parts.append(f"It takes {input_desc} and returns {output_desc} in a straightforward {num_steps}-step process.")
        elif num_steps < 15:
            parts.append(f"It processes {input_desc} through {num_steps} steps to produce {output_desc}.")
        else:
            parts.append(f"It implements a complex process with {num_steps} steps, taking {input_desc} and returning {output_desc}.")

        return " ".join(parts)

    def _generate_detailed(self, execution_trace: Optional[Dict[int, Any]] = None) -> str:
        """Generate detailed step-by-step walkthrough per D-06, D-07."""
        lines = []
        lines.append(f"Detailed walkthrough of {self.algorithm.name}:")
        lines.append("")

        for step in self.algorithm.steps:
            step_desc = self._explain_step_by_type(step)
            lines.append(f"Step {step.id}: {step_desc}")

            # Add execution values if available
            if execution_trace and step.id in execution_trace:
                values = execution_trace[step.id]
                if values:
                    lines.append(f"  At this point: {self._format_values(values)}")

            lines.append("")

        return "\n".join(lines)

    def _generate_step_explanations(
        self,
        execution_trace: Optional[Dict[int, Any]] = None
    ) -> List[StepExplanation]:
        """Generate explanations for all steps."""
        explanations = []
        for step in self.algorithm.steps:
            desc = self._explain_step_by_type(step)
            notation = self._extract_mathematical_notation(step)

            # Get execution values if available
            inputs = {}
            outputs = {}
            if execution_trace and step.id in execution_trace:
                trace_data = execution_trace[step.id]
                if isinstance(trace_data, dict):
                    for var in step.inputs:
                        if var in trace_data:
                            inputs[var] = trace_data[var]
                    for var in step.outputs:
                        if var in trace_data:
                            outputs[var] = trace_data[var]

            explanations.append(StepExplanation(
                step_id=step.id,
                description=desc,
                inputs=inputs,
                outputs=outputs,
                mathematical_notation=notation
            ))

        return explanations

    def _explain_step_by_type(self, step: Step) -> str:
        """Generate explanation based on step type."""
        if step.type == StepType.ASSIGNMENT:
            return self._explain_assignment(step)
        elif step.type in (StepType.LOOP_FOR, StepType.LOOP_WHILE):
            return self._explain_loop(step)
        elif step.type == StepType.CONDITIONAL:
            return self._explain_conditional(step)
        elif step.type == StepType.RETURN:
            return self._explain_return(step)
        elif step.type == StepType.CALL:
            return self._explain_call(step)
        else:
            return step.description

    def _explain_assignment(self, step: Step) -> str:
        """Explain an assignment step."""
        if step.expression:
            return f"Assign {step.expression}"
        elif step.outputs:
            return f"Set {', '.join(step.outputs)} to new values"
        return step.description

    def _explain_loop(self, step: Step) -> str:
        """Explain a loop step."""
        if step.iter_var and step.iter_range:
            return f"Loop with {step.iter_var} in {step.iter_range}, processing {len(step.body)} step(s)"
        elif step.condition:
            return f"While {step.condition}, repeat {len(step.body)} step(s)"
        return f"Iterate through {len(step.body)} step(s)"

    def _explain_conditional(self, step: Step) -> str:
        """Explain a conditional step."""
        if step.condition:
            has_else = len(step.else_body) > 0
            else_part = " with alternative steps" if has_else else ""
            return f"If {step.condition}, execute {len(step.body)} step(s){else_part}"
        return f"Branch based on condition, executing {len(step.body)} step(s)"

    def _explain_return(self, step: Step) -> str:
        """Explain a return step."""
        if step.expression:
            return f"Return {step.expression}"
        elif step.inputs:
            return f"Return {', '.join(step.inputs)}"
        return "Return result"

    def _explain_call(self, step: Step) -> str:
        """Explain a function call step."""
        if step.call_target:
            args = f" with arguments {step.arguments}" if step.arguments else ""
            return f"Call {step.call_target}{args}"
        return step.description

    def _extract_mathematical_notation(self, step: Step) -> Optional[str]:
        """Extract mathematical notation from step per D-142."""
        if step.expression:
            # Check for subscript notation (x_i, etc.)
            if "_" in step.expression or "^" in step.expression:
                return step.expression
        if step.description and ("_" in step.description or "^" in step.description):
            return step.description
        return None

    def _format_values(self, values: Dict[str, Any]) -> str:
        """Format execution values for display."""
        parts = []
        for name, value in values.items():
            if isinstance(value, (list, tuple)) and len(value) > 3:
                parts.append(f"{name} = [{value[0]}, ..., {value[-1]}] (len={len(value)})")
            else:
                parts.append(f"{name} = {value}")
        return ", ".join(parts)

    def _get_step_by_id(self, step_id: int) -> Optional[Step]:
        """Get step by ID."""
        for step in self.algorithm.steps:
            if step.id == step_id:
                return step
        return None


def explain_algorithm(
    algorithm: Algorithm,
    level: ExplanationLevel = ExplanationLevel.BRIEF,
    execution_trace: Optional[Dict[int, Any]] = None
) -> ExplanationResult:
    """Convenience function to explain an algorithm.

    Args:
        algorithm: Algorithm to explain
        level: Level of detail for explanation
        execution_trace: Optional execution values per step

    Returns:
        ExplanationResult with natural language explanation
    """
    explainer = AlgorithmExplainer(algorithm)
    return explainer.explain(level=level, execution_trace=execution_trace)
