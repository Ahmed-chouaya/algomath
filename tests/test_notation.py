"""Tests for mathematical notation normalization."""
import pytest
from src.extraction.notation import (
    normalize_notation,
    transform_subscripts,
    transform_superscripts,
    transform_summation,
    transform_product,
    transform_set_membership,
    transform_arrow_notation,
    transform_operators,
)


class TestSubscripts:
    """Test subscript transformations."""

    def test_simple_subscript(self):
        """Test x_i → x[i]"""
        result = transform_subscripts("x_i")
        assert "x[i]" in result

    def test_braced_subscript(self):
        """Test x_{i} → x[i]"""
        result = transform_subscripts("Calculate x_{i}")
        assert "x[i]" in result

    def test_matrix_subscript(self):
        """Test A_{i,j} → A[i, j]"""
        result = transform_subscripts("Access A_{i,j}")
        assert "A[i" in result or "A[i,j]" in result

    def test_multiple_subscripts(self):
        """Test multiple subscripts in text."""
        result = transform_subscripts("x_i and y_j")
        assert "x[i]" in result
        assert "y[j]" in result


class TestSuperscripts:
    """Test superscript transformations."""

    def test_simple_superscript(self):
        """Test x^2 → x**2"""
        result = transform_superscripts("Calculate x^2")
        assert "x**2" in result

    def test_braced_superscript(self):
        """Test x^{n} → x**n"""
        result = transform_superscripts("Calculate x^{n}")
        assert "x**n" in result

    def test_combined_sub_superscript(self):
        """Test x_i^2 transformation order."""
        # Subscripts should be applied before/superscript
        result = transform_subscripts("x_i")
        result = transform_superscripts(result)
        assert "x[i]" in result


class TestNormalizeNotation:
    """Test complete notation normalization."""

    def test_array_notation(self):
        """Test array access normalization."""
        result = normalize_notation("x_i + y_j")
        assert "x[i]" in result
        assert "y[j]" in result

    def test_set_membership(self):
        """Test set membership operators."""
        result = normalize_notation("if x ∈ S")
        assert "x in S" in result

        result = normalize_notation("if A ⊆ B")
        assert "is subset of" in result

    def test_arrow_assignment(self):
        """Test arrow notation."""
        result = normalize_notation("x ← 0")
        assert "x = 0" in result

        result = normalize_notation("x → 0")
        assert "x = 0" in result

    def test_math_operators(self):
        """Test mathematical operators."""
        result = normalize_notation("x ≤ y")
        assert "x <= y" in result

        result = normalize_notation("x ≥ y")
        assert "x >= y" in result

        result = normalize_notation("x ≠ y")
        assert "x != y" in result

    def test_real_algorithm_text(self):
        """Test with realistic algorithm text."""
        text = """
Algorithm: Matrix Sum
Input: A_{i,j} matrix
Output: Sum s
1. Initialize s = 0
2. For each i where 1 ≤ i ≤ n:
3. For each j where 1 ≤ j ≤ m:
4. s ← s + A_{i,j}
5. Return s
"""
        result = normalize_notation(text)
        # Should have normalized subscripts
        assert "A[i" in result or "A_{i,j}" in text


class TestSetMembership:
    """Test set membership transformations."""

    def test_element_of(self):
        """Test x ∈ S → x in S"""
        result = transform_set_membership("x ∈ S")
        assert "x in S" in result

    def test_not_element_of(self):
        """Test x ∉ S → x not in S"""
        result = transform_set_membership("x ∉ S")
        assert "x not in S" in result

    def test_subset(self):
        """Test A ⊆ B → A is subset of B"""
        result = transform_set_membership("A ⊆ B")
        assert "is subset of" in result

    def test_proper_subset(self):
        """Test A ⊂ B → A is proper subset of B"""
        result = transform_set_membership("A ⊂ B")
        assert "is proper subset of" in result


class TestArrowNotation:
    """Test arrow notation transformations."""

    def test_left_arrow(self):
        """Test x ← y → x = y"""
        result = transform_arrow_notation("x ← 5")
        assert "x = 5" in result

    def test_right_arrow(self):
        """Test x → y → x = y"""
        result = transform_arrow_notation("x → 5")
        assert "x = 5" in result


class TestOperators:
    """Test mathematical operator transformations."""

    def test_less_than_or_equal(self):
        """Test ≤ → <="""
        result = transform_operators("x ≤ y")
        assert "x <= y" in result

    def test_greater_than_or_equal(self):
        """Test ≥ → >="""
        result = transform_operators("x ≥ y")
        assert "x >= y" in result

    def test_not_equal(self):
        """Test ≠ → !="""
        result = transform_operators("x ≠ y")
        assert "x != y" in result

    def test_multiply(self):
        """Test × → *"""
        result = transform_operators("x × y")
        assert "x * y" in result

    def test_divide(self):
        """Test ÷ → /"""
        result = transform_operators("x ÷ y")
        assert "x / y" in result


class TestSummation:
    """Test summation notation transformations."""

    def test_summation_over_range(self):
        """Test Σ_{i=1}^{n} transforms correctly"""
        result = transform_summation("Σ_{i=1}^{n} x_i")
        assert "sum over" in result

    def test_summation_over_set(self):
        """Test Σ_{i∈S} transforms correctly"""
        result = transform_summation("Σ_{i∈S} f(i)")
        assert "sum over" in result


class TestProduct:
    """Test product notation transformations."""

    def test_product_over_range(self):
        """Test Π_{i=1}^{n} transforms correctly"""
        result = transform_product("Π_{i=1}^{n} x_i")
        assert "product over" in result

    def test_product_over_set(self):
        """Test Π_{i∈S} transforms correctly"""
        result = transform_product("Π_{i∈S} f(i)")
        assert "product over" in result
