"""Tests for code generator."""

import ast
import pytest
from src.generation.code_generator import TemplateCodeGenerator, GeneratedCode
from src.extraction.schema import Algorithm, Step, StepType


class TestTemplateCodeGenerator:
    """Test code generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = TemplateCodeGenerator()

    def test_simple_algorithm_generation(self):
        """Test generating code for simple 3-step algorithm."""
        algorithm = Algorithm(
            name="simple_sum",
            description="Calculate sum of first n numbers",
            inputs=[{"name": "n", "description": "Input number"}],
            outputs=[{"name": "result", "description": "The sum"}],
            steps=[
                Step(id=1, type=StepType.ASSIGNMENT, description="Initialize result", outputs=["result"], expression="0"),
                Step(id=2, type=StepType.LOOP_FOR, description="Loop through numbers", 
                     iter_var="i", iter_range="range(n)", body=[3]),
                Step(id=3, type=StepType.ASSIGNMENT, description="Add to result", outputs=["result"], 
                     expression="result + i"),
                Step(id=4, type=StepType.RETURN, description="Return result", expression="result"),
            ]
        )
        
        result = self.generator.generate(algorithm)
        assert isinstance(result, GeneratedCode)
        assert result.algorithm_name == "simple_sum"
        
        # Check syntax validity
        try:
            ast.parse(result.source)
            is_valid = True
        except SyntaxError:
            is_valid = False
        assert is_valid

    def test_function_signature_generation(self):
        """Test that function signature is generated."""
        algorithm = Algorithm(
            name="test_algo",
            description="Test algorithm",
            inputs=[{"name": "n", "description": "Size"}],
            outputs=[{"name": "result", "description": "Result"}],
            steps=[
                Step(id=1, type=StepType.RETURN, description="Return", expression="n"),
            ]
        )
        
        result = self.generator.generate(algorithm)
        assert "def test_algo" in result.source
        assert "n: int" in result.source

    def test_docstring_generation(self):
        """Test that docstring is generated."""
        algorithm = Algorithm(
            name="test_algo",
            description="Test algorithm description",
            inputs=[{"name": "n", "description": "Input size"}],
            outputs=[{"name": "result", "description": "Output result"}],
            steps=[
                Step(id=1, type=StepType.RETURN, description="Return", expression="n"),
            ]
        )
        
        result = self.generator.generate(algorithm)
        assert '"""' in result.source
        assert "Test algorithm description" in result.source

    def test_imports_generation(self):
        """Test that necessary imports are generated."""
        algorithm = Algorithm(
            name="matrix_mult",
            description="Matrix multiplication",
            inputs=[{"name": "A", "description": "First matrix"}],
            outputs=[{"name": "result", "description": "Result matrix"}],
            steps=[
                Step(id=1, type=StepType.ASSIGNMENT, description="Multiply", outputs=["result"], expression="A @ A.T"),
                Step(id=2, type=StepType.RETURN, description="Return", expression="result"),
            ]
        )
        
        result = self.generator.generate(algorithm)
        # Should include typing imports
        assert "from typing import" in result.source or "import numpy" in result.source

    def test_validation_result(self):
        """Test that validation result is included."""
        algorithm = Algorithm(
            name="test_algo",
            description="Test algorithm",
            inputs=[{"name": "n", "description": "Size"}],
            outputs=[{"name": "result", "description": "Result"}],
            steps=[
                Step(id=1, type=StepType.RETURN, description="Return", expression="n"),
            ]
        )
        
        result = self.generator.generate(algorithm)
        assert result.validation_result is not None

    def test_execution_guard(self):
        """Test that execution guard is added."""
        algorithm = Algorithm(
            name="test_algo",
            description="Test algorithm",
            inputs=[],
            outputs=[{"name": "result", "description": "Result"}],
            steps=[
                Step(id=1, type=StepType.RETURN, description="Return", expression="0"),
            ]
        )
        
        result = self.generator.generate(algorithm)
        assert '__name__ == "__main__"' in result.source

    def test_snake_case_conversion(self):
        """Test that algorithm names are converted to snake_case."""
        algorithm = Algorithm(
            name="TestAlgorithm",
            description="Test algorithm",
            inputs=[],
            outputs=[{"name": "result", "description": "Result"}],
            steps=[
                Step(id=1, type=StepType.RETURN, description="Return", expression="0"),
            ]
        )
        
        result = self.generator.generate(algorithm)
        assert "def test_algorithm" in result.source
