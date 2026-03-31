"""Tests for the algorithm explainer module."""

import pytest
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json

from src.extraction.schema import Algorithm, Step, StepType
from src.verification.explainer import (
    AlgorithmExplainer,
    ExplanationResult,
    ExplanationLevel,
    StepExplanation,
    explain_algorithm,
)


class TestExplainAlgorithm:
    """Test explain_algorithm function and AlgorithmExplainer."""

    def create_simple_algorithm(self):
        """Create a simple algorithm for testing."""
        steps = [
            Step(
                id=1,
                type=StepType.ASSIGNMENT,
                description="Initialize result to 0",
                inputs=[],
                outputs=["result"],
                expression="result = 0"
            ),
            Step(
                id=2,
                type=StepType.RETURN,
                description="Return the result",
                inputs=["result"],
                outputs=[],
                expression="return result"
            ),
        ]
        return Algorithm(
            name="SimpleTest",
            description="A simple test algorithm",
            inputs=[{"name": "n", "type": "int"}],
            outputs=[{"name": "result", "type": "int"}],
            steps=steps,
            source_text=""
        )

    def create_complex_algorithm(self):
        """Create a complex algorithm with loops and conditionals."""
        steps = [
            Step(
                id=1,
                type=StepType.ASSIGNMENT,
                description="Initialize sum to 0",
                inputs=[],
                outputs=["sum"],
                expression="sum = 0"
            ),
            Step(
                id=2,
                type=StepType.LOOP_FOR,
                description="Iterate over range n",
                inputs=["n"],
                outputs=["i"],
                iter_var="i",
                iter_range="range(n)",
                body=[3]
            ),
            Step(
                id=3,
                type=StepType.ASSIGNMENT,
                description="Add i to sum",
                inputs=["sum", "i"],
                outputs=["sum"],
                expression="sum = sum + i"
            ),
            Step(
                id=4,
                type=StepType.CONDITIONAL,
                description="Check if sum is positive",
                inputs=["sum"],
                outputs=[],
                condition="sum > 0",
                body=[5],
                else_body=[6]
            ),
            Step(
                id=5,
                type=StepType.RETURN,
                description="Return positive sum",
                inputs=["sum"],
                outputs=[],
                expression="return sum"
            ),
            Step(
                id=6,
                type=StepType.RETURN,
                description="Return zero",
                inputs=[],
                outputs=[],
                expression="return 0"
            ),
        ]
        return Algorithm(
            name="ComplexTest",
            description="A complex test algorithm with loops",
            inputs=[{"name": "n", "type": "int"}],
            outputs=[{"name": "result", "type": "int"}],
            steps=steps,
            source_text=""
        )

    def test_explain_algorithm_returns_brief_summary(self):
        """Test 1: explain_algorithm() returns brief summary (1-2 sentences) per D-05."""
        algorithm = self.create_simple_algorithm()
        result = explain_algorithm(algorithm, level=ExplanationLevel.BRIEF)

        assert isinstance(result, ExplanationResult)
        assert len(result.summary) > 0
        # Should be 1-2 sentences (rough check)
        sentence_count = result.summary.count('.') + result.summary.count('!') + result.summary.count('?')
        assert sentence_count >= 1 and sentence_count <= 3  # Allow 1-3 sentences
        assert "SimpleTest" in result.summary or "algorithm" in result.summary.lower()

    def test_explain_algorithm_detailed_returns_step_by_step(self):
        """Test 2: explain_algorithm(detailed=True) returns step-by-step walkthrough per D-06."""
        algorithm = self.create_simple_algorithm()
        result = explain_algorithm(algorithm, level=ExplanationLevel.DETAILED)

        assert isinstance(result, ExplanationResult)
        assert result.detailed_explanation is not None
        assert len(result.detailed_explanation) > len(result.summary)
        # Detailed should mention steps
        assert "step" in result.detailed_explanation.lower() or "Step" in result.detailed_explanation

    def test_step_explanations_reference_execution_values(self):
        """Test 3: Step explanations reference actual execution values when available per D-07."""
        algorithm = self.create_simple_algorithm()
        execution_trace = {
            1: {"result": 0},
            2: {"result": 0}
        }

        explainer = AlgorithmExplainer(algorithm)
        result = explainer.explain(
            level=ExplanationLevel.DETAILED,
            execution_trace=execution_trace
        )

        assert result.execution_trace is not None
        assert result.execution_trace == execution_trace

        # Check step explanations include values
        for step_exp in result.step_explanations:
            if step_exp.inputs:
                assert isinstance(step_exp.inputs, dict)
            if step_exp.outputs:
                assert isinstance(step_exp.outputs, dict)

    def test_simple_algorithms_get_brief_complex_get_detailed(self):
        """Test 4: Simple algorithms get brief, complex get detailed per D-08."""
        simple = self.create_simple_algorithm()
        complex_alg = self.create_complex_algorithm()

        simple_explainer = AlgorithmExplainer(simple)
        complex_explainer = AlgorithmExplainer(complex_alg)

        # Simple algorithm should have low complexity score
        assert simple_explainer._calculate_complexity() < 0.5

        # Complex algorithm should have high complexity score (loops + conditionals)
        assert complex_explainer._calculate_complexity() >= 0.3

        # Recommendations should match
        simple_result = simple_explainer.explain()
        complex_result = complex_explainer.explain()

        assert simple_result.recommended_level == ExplanationLevel.BRIEF
        assert complex_result.recommended_level == ExplanationLevel.DETAILED

    def test_explanation_preserves_mathematical_notation(self):
        """Test 5: Explanation preserves original paper notation if available per D-142."""
        steps = [
            Step(
                id=1,
                type=StepType.ASSIGNMENT,
                description="Set x_i = x_{i-1} + 1",
                inputs=["x_{i-1}"],
                outputs=["x_i"],
                expression="x_i = x_{i-1} + 1"
            ),
        ]
        algorithm = Algorithm(
            name="MathTest",
            description="Test with notation",
            inputs=[],
            outputs=[],
            steps=steps,
            source_text=""
        )

        explainer = AlgorithmExplainer(algorithm)
        step_exp = explainer.explain_step(1)

        assert step_exp.mathematical_notation is not None
        assert "x_i" in step_exp.mathematical_notation or "x_" in step_exp.description

    def test_explanation_result_is_json_serializable(self):
        """Test 6: ExplanationResult is JSON-serializable for persistence."""
        algorithm = self.create_simple_algorithm()
        result = explain_algorithm(algorithm)

        # Test to_dict
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert "summary" in result_dict
        assert "complexity_score" in result_dict

        # Test to_json
        result_json = result.to_json()
        assert isinstance(result_json, str)

        # Should be valid JSON
        parsed = json.loads(result_json)
        assert parsed["summary"] == result.summary
        assert parsed["complexity_score"] == result.complexity_score


class TestExplanationResult:
    """Test ExplanationResult dataclass functionality."""

    def test_explanation_result_creation(self):
        """Test creating ExplanationResult with all fields."""
        step_exps = [
            StepExplanation(
                step_id=1,
                description="Test step",
                inputs={},
                outputs={"result": 42},
                mathematical_notation="x = 42"
            )
        ]

        result = ExplanationResult(
            summary="Test summary",
            detailed_explanation="Detailed explanation here",
            step_explanations=step_exps,
            complexity_score=0.5,
            recommended_level=ExplanationLevel.BRIEF,
            execution_trace={1: {"result": 42}}
        )

        assert result.summary == "Test summary"
        assert result.detailed_explanation == "Detailed explanation here"
        assert len(result.step_explanations) == 1
        assert result.complexity_score == 0.5

    def test_step_explanation_creation(self):
        """Test creating StepExplanation."""
        step_exp = StepExplanation(
            step_id=1,
            description="Initialize x",
            inputs={},
            outputs={"x": 0},
            mathematical_notation="x_0 = 0"
        )

        assert step_exp.step_id == 1
        assert step_exp.description == "Initialize x"
        assert step_exp.outputs["x"] == 0


class TestAlgorithmExplainerMethods:
    """Test AlgorithmExplainer internal methods."""

    def test_complexity_calculation(self):
        """Test complexity scoring."""
        steps = [
            Step(id=i, type=StepType.ASSIGNMENT, description=f"Step {i}", inputs=[], outputs=[])
            for i in range(20)
        ]
        # Add nested loops for higher complexity
        steps.append(Step(
            id=21,
            type=StepType.LOOP_FOR,
            description="Outer loop",
            inputs=[],
            outputs=[],
            body=[22]
        ))
        steps.append(Step(
            id=22,
            type=StepType.LOOP_FOR,
            description="Inner loop",
            inputs=[],
            outputs=[],
            body=[]
        ))

        algorithm = Algorithm(
            name="Complex",
            description="Complex algo",
            inputs=[],
            outputs=[],
            steps=steps,
            source_text=""
        )

        explainer = AlgorithmExplainer(algorithm)
        complexity = explainer._calculate_complexity()

        # Should be high due to step count and nested loops
        assert complexity > 0.5
        assert complexity <= 1.0

    def test_explain_step_assignment(self):
        """Test explaining an assignment step."""
        step = Step(
            id=1,
            type=StepType.ASSIGNMENT,
            description="Set x to 5",
            inputs=[],
            outputs=["x"],
            expression="x = 5"
        )
        algorithm = Algorithm(
            name="Test",
            description="Test",
            inputs=[],
            outputs=[],
            steps=[step],
            source_text=""
        )

        explainer = AlgorithmExplainer(algorithm)
        explanation = explainer._explain_assignment(step)

        assert len(explanation) > 0
        assert "5" in explanation or "assign" in explanation.lower()

    def test_explain_step_loop(self):
        """Test explaining a loop step."""
        step = Step(
            id=1,
            type=StepType.LOOP_FOR,
            description="Loop through items",
            inputs=["items"],
            outputs=["item"],
            iter_var="item",
            iter_range="items",
            body=[2]
        )
        algorithm = Algorithm(
            name="Test",
            description="Test",
            inputs=[],
            outputs=[],
            steps=[step],
            source_text=""
        )

        explainer = AlgorithmExplainer(algorithm)
        explanation = explainer._explain_loop(step)

        assert len(explanation) > 0
        assert "loop" in explanation.lower() or "iterate" in explanation.lower()

    def test_explain_step_conditional(self):
        """Test explaining a conditional step."""
        step = Step(
            id=1,
            type=StepType.CONDITIONAL,
            description="Check if positive",
            inputs=["x"],
            outputs=[],
            condition="x > 0",
            body=[2],
            else_body=[3]
        )
        algorithm = Algorithm(
            name="Test",
            description="Test",
            inputs=[],
            outputs=[],
            steps=[step],
            source_text=""
        )

        explainer = AlgorithmExplainer(algorithm)
        explanation = explainer._explain_conditional(step)

        assert len(explanation) > 0
        assert "condition" in explanation.lower() or "if" in explanation.lower()


class TestExplainAlgorithmFunction:
    """Test the standalone explain_algorithm function."""

    def test_explain_algorithm_function(self):
        """Test explain_algorithm convenience function."""
        steps = [
            Step(
                id=1,
                type=StepType.ASSIGNMENT,
                description="Set x = 1",
                inputs=[],
                outputs=["x"],
                expression="x = 1"
            ),
        ]
        algorithm = Algorithm(
            name="Simple",
            description="Simple algo",
            inputs=[],
            outputs=[],
            steps=steps,
            source_text=""
        )

        result = explain_algorithm(algorithm)
        assert isinstance(result, ExplanationResult)
        assert len(result.summary) > 0

    def test_explain_algorithm_with_execution_trace(self):
        """Test explain_algorithm with execution trace."""
        steps = [
            Step(
                id=1,
                type=StepType.ASSIGNMENT,
                description="Set x = 1",
                inputs=[],
                outputs=["x"],
                expression="x = 1"
            ),
        ]
        algorithm = Algorithm(
            name="Simple",
            description="Simple algo",
            inputs=[],
            outputs=[],
            steps=steps,
            source_text=""
        )
        trace = {1: {"x": 1}}

        result = explain_algorithm(algorithm, execution_trace=trace)
        assert result.execution_trace == trace
