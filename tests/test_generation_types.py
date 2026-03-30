"""Tests for type inference utilities."""

import pytest
from src.generation.types import TypeInferrer, FunctionSignature, PythonType


class TestTypeInferrer:
    """Test type inference heuristics."""

    def setup_method(self):
        """Set up test fixtures."""
        self.inferrer = TypeInferrer()

    def test_infer_int_from_n(self):
        """Test that 'n' infers to int."""
        result = self.inferrer.infer_variable_type("n", {})
        assert result == "int"

    def test_infer_int_from_count(self):
        """Test that 'count' infers to int."""
        result = self.inferrer.infer_variable_type("count", {})
        assert result == "int"

    def test_infer_int_from_index(self):
        """Test that 'index' infers to int."""
        result = self.inferrer.infer_variable_type("index", {})
        assert result == "int"

    def test_infer_int_from_m(self):
        """Test that 'm' infers to int."""
        result = self.inferrer.infer_variable_type("m", {})
        assert result == "int"

    def test_infer_int_from_i_j_k(self):
        """Test that i, j, k infer to int."""
        assert self.inferrer.infer_variable_type("i", {}) == "int"
        assert self.inferrer.infer_variable_type("j", {}) == "int"
        assert self.inferrer.infer_variable_type("k", {}) == "int"

    def test_infer_ndarray_from_matrix(self):
        """Test that 'matrix' infers to np.ndarray."""
        result = self.inferrer.infer_variable_type("matrix", {})
        assert result == "np.ndarray"

    def test_infer_ndarray_from_A(self):
        """Test that 'A' infers to np.ndarray."""
        result = self.inferrer.infer_variable_type("A", {})
        assert result == "np.ndarray"

    def test_infer_ndarray_from_grid(self):
        """Test that 'grid' infers to np.ndarray."""
        result = self.inferrer.infer_variable_type("grid", {})
        assert result == "np.ndarray"

    def test_infer_ndarray_from_vector(self):
        """Test that 'vector' infers to np.ndarray."""
        result = self.inferrer.infer_variable_type("vector", {})
        assert result == "np.ndarray"

    def test_infer_float_from_epsilon(self):
        """Test that 'epsilon' infers to float."""
        result = self.inferrer.infer_variable_type("epsilon", {})
        assert result == "float"

    def test_infer_float_from_delta(self):
        """Test that 'delta' infers to float."""
        result = self.inferrer.infer_variable_type("delta", {})
        assert result == "float"

    def test_infer_float_from_tolerance(self):
        """Test that 'tolerance' infers to float."""
        result = self.inferrer.infer_variable_type("tolerance", {})
        assert result == "float"

    def test_infer_float_from_threshold(self):
        """Test that 'threshold' infers to float."""
        result = self.inferrer.infer_variable_type("threshold", {})
        assert result == "float"

    def test_infer_list_from_items(self):
        """Test that 'items' infers to List."""
        result = self.inferrer.infer_variable_type("items", {})
        assert result == "List"

    def test_infer_list_from_nodes(self):
        """Test that 'nodes' infers to List."""
        result = self.inferrer.infer_variable_type("nodes", {})
        assert result == "List"

    def test_infer_list_from_edges(self):
        """Test that 'edges' infers to List."""
        result = self.inferrer.infer_variable_type("edges", {})
        assert result == "List"

    def test_infer_list_from_vertices(self):
        """Test that 'vertices' infers to List."""
        result = self.inferrer.infer_variable_type("vertices", {})
        assert result == "List"

    def test_infer_bool_from_visited(self):
        """Test that 'visited' infers to bool."""
        result = self.inferrer.infer_variable_type("visited", {})
        assert result == "bool"

    def test_infer_bool_from_found(self):
        """Test that 'found' infers to bool."""
        result = self.inferrer.infer_variable_type("found", {})
        assert result == "bool"

    def test_infer_bool_from_is_valid(self):
        """Test that 'is_valid' infers to bool."""
        result = self.inferrer.infer_variable_type("is_valid", {})
        assert result == "bool"

    def test_infer_function_returns_list_float(self):
        """Test function signature inference with result outputs."""
        from src.extraction.schema import Algorithm, Step, StepType
        
        algorithm = Algorithm(
            name="test_algorithm",
            description="Test algorithm",
            inputs=[{"name": "n", "description": "Size"}],
            outputs=[{"name": "result", "description": "The result"}],
            steps=[
                Step(id=1, type=StepType.ASSIGNMENT, description="Init", outputs=["result"])
            ]
        )
        
        sig = self.inferrer.infer_function_signature(algorithm)
        assert sig.return_type == "List[float]"

    def test_infer_function_returns_list_float_for_path(self):
        """Test function returns List[float] for path output."""
        from src.extraction.schema import Algorithm, Step, StepType
        
        algorithm = Algorithm(
            name="test_algorithm",
            description="Test algorithm",
            inputs=[{"name": "graph", "description": "Input graph"}],
            outputs=[{"name": "path", "description": "The path"}],
            steps=[
                Step(id=1, type=StepType.ASSIGNMENT, description="Init", outputs=["path"])
            ]
        )
        
        sig = self.inferrer.infer_function_signature(algorithm)
        assert sig.return_type == "List[float]"

    def test_infer_function_returns_list_float_for_distances(self):
        """Test function returns List[float] for distances output."""
        from src.extraction.schema import Algorithm, Step, StepType
        
        algorithm = Algorithm(
            name="test_algorithm",
            description="Test algorithm",
            inputs=[{"name": "graph", "description": "Input graph"}],
            outputs=[{"name": "distances", "description": "Distances"}],
            steps=[
                Step(id=1, type=StepType.ASSIGNMENT, description="Init", outputs=["distances"])
            ]
        )
        
        sig = self.inferrer.infer_function_signature(algorithm)
        assert sig.return_type == "List[float]"

    def test_format_type_hint_with_optional(self):
        """Test Optional type formatting."""
        result = self.inferrer.format_type_hint("int", optional=True)
        assert result == "Optional[int]"

    def test_format_type_hint_without_optional(self):
        """Test non-optional type formatting."""
        result = self.inferrer.format_type_hint("int", optional=False)
        assert result == "int"

    def test_infer_unknown_returns_Any(self):
        """Test that unknown variables return Any."""
        result = self.inferrer.infer_variable_type("xyz_unknown", {})
        assert result == "Any"
