"""Tests for code templates."""

import pytest
from src.generation.templates import TemplateRegistry, CodeTemplates
from src.extraction.schema import Step, StepType


class TestTemplateRegistry:
    """Test template registry functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = TemplateRegistry()

    def test_assignment_template(self):
        """Test StepType.ASSIGNMENT has template."""
        template = self.registry.get(StepType.ASSIGNMENT)
        assert "{target}" in template
        assert "{expression}" in template

    def test_loop_for_template(self):
        """Test StepType.LOOP_FOR has template."""
        template = self.registry.get(StepType.LOOP_FOR)
        assert "{iter_var}" in template
        assert "{iter_range}" in template
        assert "{body}" in template

    def test_loop_while_template(self):
        """Test StepType.LOOP_WHILE has template."""
        template = self.registry.get(StepType.LOOP_WHILE)
        assert "{condition}" in template
        assert "{body}" in template

    def test_conditional_template(self):
        """Test StepType.CONDITIONAL has template."""
        template = self.registry.get(StepType.CONDITIONAL)
        assert "{condition}" in template
        assert "{if_body}" in template

    def test_return_template(self):
        """Test StepType.RETURN has template."""
        template = self.registry.get(StepType.RETURN)
        assert "{expression}" in template

    def test_format_assignment_step(self):
        """Test formatting an assignment step."""
        step = Step(
            id=1,
            type=StepType.ASSIGNMENT,
            description="Initialize n",
            outputs=["n"],
            expression="5"
        )
        result = self.registry.format_step(step, indent=0)
        assert "n = 5" in result

    def test_format_return_step(self):
        """Test formatting a return step."""
        step = Step(
            id=1,
            type=StepType.RETURN,
            description="Return result",
            inputs=["result"],
            expression="result"
        )
        result = self.registry.format_step(step, indent=0)
        assert "return result" in result

    def test_indentation(self):
        """Test code indentation."""
        code = "x = 1\ny = 2"
        result = self.registry.indent_lines(code, level=1)
        assert result.startswith("    x = 1")
        assert "    y = 2" in result

    def test_register_custom_template(self):
        """Test registering custom template."""
        self.registry.register(StepType.ASSIGNMENT, "{target} := {expression}")
        template = self.registry.get(StepType.ASSIGNMENT)
        assert template == "{target} := {expression}"


class TestCodeTemplates:
    """Test code template collections."""

    def test_templates_exist(self):
        """Test that CodeTemplates class exists."""
        templates = CodeTemplates()
        assert templates is not None

    def test_summation_template(self):
        """Test summation operator template."""
        templates = CodeTemplates()
        assert hasattr(templates, 'summation')
        assert "sum" in templates.summation

    def test_product_template(self):
        """Test product operator template."""
        templates = CodeTemplates()
        assert hasattr(templates, 'product')
        assert "math.prod" in templates.product

    def test_sqrt_template(self):
        """Test square root template."""
        templates = CodeTemplates()
        assert hasattr(templates, 'sqrt')
        assert "math.sqrt" in templates.sqrt

    def test_abs_template(self):
        """Test absolute value template."""
        templates = CodeTemplates()
        assert hasattr(templates, 'abs')
        assert "abs" in templates.abs
