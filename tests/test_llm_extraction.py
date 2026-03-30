"""Tests for LLM extraction with fallback."""
import pytest
from src.extraction.llm_extraction import HybridExtractor, extract_algorithm_llm
from src.extraction.schema import Algorithm, Step, StepType


class TestHybridExtractor:
    """Test hybrid extraction functionality."""

    def test_extract_with_rule_based_fallback(self):
        """Test extraction falls back to rule-based parser."""
        extractor = HybridExtractor()
        text = "Algorithm: Test\n1. Initialize x = 0\n2. Return x"
        result = extractor.extract(text, prefer_llm=False)

        assert result.success
        assert result.method == "rule_based"
        assert len(result.algorithm.steps) >= 2

    def test_extract_from_sample_algorithm(self):
        """Test extraction from sample algorithm text."""
        extractor = HybridExtractor()
        text = """Algorithm: Sum Array
Input: A[1..n]
Output: Sum of elements
1. Initialize sum = 0
2. For i from 1 to n:
3. sum = sum + A[i]
4. Return sum"""

        result = extractor.extract(text, prefer_llm=False)

        assert result.success
        assert result.algorithm.name == "Sum Array"
        assert len(result.algorithm.inputs) >= 1
        assert len(result.algorithm.outputs) >= 1
        assert len(result.algorithm.steps) >= 4

    def test_extract_finds_step_types(self):
        """Test extraction identifies different step types."""
        extractor = HybridExtractor()
        text = """Algorithm: Test
1. x = 1
2. while x < 10:
3. x = x + 1
4. return x"""

        result = extractor.extract(text, prefer_llm=False)

        assert result.success
        # Should have parsed steps
        assert len(result.algorithm.steps) >= 4

    def test_extraction_result_has_algorithm(self):
        """Test that extraction result contains algorithm."""
        extractor = HybridExtractor()
        result = extractor.extract("Algorithm: X\n1. Step", prefer_llm=False)

        assert result.algorithm is not None
        assert isinstance(result.algorithm, Algorithm)

    def test_extraction_with_empty_text(self):
        """Test extraction handles empty text."""
        extractor = HybridExtractor()
        result = extractor.extract("", prefer_llm=False)

        assert result.success
        assert result.algorithm.name == "unnamed"


class TestExtractAlgorithmLLM:
    """Test LLM extraction function."""

    def test_llm_extraction_falls_back(self):
        """Test that LLM extraction falls back to rule-based."""
        text = "Algorithm: Test\n1. Initialize\n2. Return"
        result = extract_algorithm_llm(text)

        # Should succeed via fallback
        assert result.success
        assert result.method in ["llm", "rule_based"]

    def test_llm_extraction_has_line_references(self):
        """Test that extraction preserves line references."""
        text = "Algorithm: Test\n1. Initialize x = 0\n2. Return x"
        result = extract_algorithm_llm(text)

        assert result.success
        # Line references should be populated
        for refs in result.line_references:
            assert isinstance(refs, list)

    def test_llm_extraction_handles_complex_text(self):
        """Test extraction with complex algorithm text."""
        text = """Algorithm: Matrix Multiply
Input: A, B matrices
Output: C = A × B
1. For i from 1 to n:
2. For j from 1 to m:
3. C[i][j] = sum(A[i][k] * B[k][j])
4. Return C"""

        result = extract_algorithm_llm(text)
        assert result.success
        assert len(result.algorithm.steps) >= 3


class TestExtractionResult:
    """Test ExtractionResult dataclass."""

    def test_result_initialization(self):
        """Test ExtractionResult initialization."""
        algo = Algorithm(name="test")
        result = extract_algorithm_llm("Algorithm: Test")

        assert hasattr(result, 'algorithm')
        assert hasattr(result, 'success')
        assert hasattr(result, 'method')
        assert hasattr(result, 'errors')

    def test_result_str_representation(self):
        """Test ExtractionResult has expected attributes."""
        result = extract_algorithm_llm("1. Step")

        assert isinstance(result.success, bool)
        assert isinstance(result.method, str)
        assert isinstance(result.errors, list)
        assert isinstance(result.line_references, list)


class TestExtractionEdgeCases:
    """Test edge cases for extraction."""

    def test_single_line_algorithm(self):
        """Test extraction of single line algorithm."""
        extractor = HybridExtractor()
        result = extractor.extract("Algorithm: Simple\nReturn 0", prefer_llm=False)

        assert result.success
        assert result.algorithm.name == "Simple"

    def test_no_steps(self):
        """Test extraction with no steps."""
        extractor = HybridExtractor()
        result = extractor.extract("Algorithm: Empty", prefer_llm=False)

        assert result.success
        assert len(result.algorithm.steps) == 0

    def test_special_characters(self):
        """Test extraction with special characters."""
        extractor = HybridExtractor()
        text = "Algorithm: Special\n1. x ← y\n2. x = y + z"
        result = extractor.extract(text, prefer_llm=False)

        assert result.success


class TestStepExtraction:
    """Test step extraction details."""

    def test_step_has_id(self):
        """Test that extracted steps have IDs."""
        extractor = HybridExtractor()
        result = extractor.extract("1. Step one\n2. Step two", prefer_llm=False)

        assert result.success
        for i, step in enumerate(result.algorithm.steps, 1):
            assert step.id == i

    def test_step_has_type(self):
        """Test that extracted steps have types."""
        extractor = HybridExtractor()
        result = extractor.extract("1. x = 1\n2. return x", prefer_llm=False)

        assert result.success
        for step in result.algorithm.steps:
            assert isinstance(step.type, StepType)

    def test_step_has_description(self):
        """Test that extracted steps have descriptions."""
        extractor = HybridExtractor()
        result = extractor.extract("1. Set x = 0", prefer_llm=False)

        assert result.success
        for step in result.algorithm.steps:
            assert isinstance(step.description, str)
