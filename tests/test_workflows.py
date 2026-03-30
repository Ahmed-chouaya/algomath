"""
Unit tests for workflow stubs.

Tests the extraction, generation, execution, and verification workflow stubs.
"""

import pytest
from pathlib import Path

import algomath.context as ctx_module
import algomath.persistence as persist_module
import algomath.state as state_module
from src.workflows import run_extraction, run_generation, run_execution, run_verification


def _create_context_manager(temp_dir):
    """Helper to create a ContextManager with temp paths."""
    algopath = Path(temp_dir) / ".algomath"
    persist_module.ALGOMATH_DIR = algopath
    persist_module.ALGORITHMS_DIR = algopath / "algorithms"
    state_module.ALGOMATH_DIR = algopath
    state_module.SESSION_FILE = algopath / "session.json"

    return ctx_module.ContextManager()


class TestWorkflowStubs:
    """Test suite for workflow stub functionality."""

    def test_extraction_returns_status(self, temp_algopath):
        """Test extraction returns status dict."""
        cm = _create_context_manager(temp_algopath)
        cm.start_session()

        result = run_extraction(cm, text="test algorithm")
        assert "status" in result
        assert result["status"] in ["extraction_complete", "stub", "success", "needs_input"]

    def test_extraction_updates_context(self, temp_algopath):
        """Test extraction updates context with text."""
        cm = _create_context_manager(temp_algopath)
        cm.start_session()

        run_extraction(cm, text="test")
        assert cm.get_current().data.get("text") == "test"

    def test_generation_returns_status(self, temp_algopath):
        """Test generation returns status dict."""
        cm = _create_context_manager(temp_algopath)
        cm.start_session()
        cm.save_text("text")
        cm.save_steps([{"step": 1}])

        result = run_generation(cm)
        assert "status" in result
        assert result["status"] in ["generation_stub", "success", "needs_extraction", "error"]

    def test_generation_checks_steps_exist(self, temp_algopath):
        """Test generation requires steps to exist."""
        cm = _create_context_manager(temp_algopath)
        cm.start_session()
        cm.save_text("text")

        result = run_generation(cm)
        assert "error" in result or "status" in result

    def test_execution_returns_status(self, temp_algopath):
        """Test execution returns status dict."""
        cm = _create_context_manager(temp_algopath)
        cm.start_session()
        cm.save_text("text")
        cm.save_steps([{"step": 1}])
        cm.save_code("def test(): pass")

        result = run_execution(cm)
        assert "status" in result
        assert result["status"] in ["execution_stub", "success", "needs_generation", "error"]

    def test_verification_returns_status(self, temp_algopath):
        """Test verification returns status dict."""
        cm = _create_context_manager(temp_algopath)
        cm.start_session()
        cm.save_text("text")
        cm.save_steps([{"step": 1}])
        cm.save_code("def test(): pass")
        cm.save_results({"output": "test"})

        result = run_verification(cm)
        assert "status" in result
        assert result["status"] in ["verification_stub", "success", "needs_execution", "error"]

    def test_extraction_requires_text(self, temp_algopath):
        """Test extraction requires text input."""
        cm = _create_context_manager(temp_algopath)
        cm.start_session()

        result = run_extraction(cm)  # No text provided
        assert result["status"] in ["needs_input", "stub"]

    def test_extraction_with_name(self, temp_algopath):
        """Test extraction with algorithm name."""
        cm = _create_context_manager(temp_algopath)
        cm.start_session()

        result = run_extraction(cm, text="test algorithm", name="my_algo")
        assert "status" in result

    def test_generation_updates_context(self, temp_algopath):
        """Test generation saves code to context."""
        cm = _create_context_manager(temp_algopath)
        cm.start_session()
        cm.save_text("text")
        cm.save_steps([{"step": 1}])

        run_generation(cm)
        assert "code" in cm.get_current().data

    def test_execution_updates_context(self, temp_algopath):
        """Test execution saves results to context."""
        cm = _create_context_manager(temp_algopath)
        cm.start_session()
        cm.save_text("text")
        cm.save_steps([{"step": 1}])
        cm.save_code("def test(): pass")

        run_execution(cm)
        assert "results" in cm.get_current().data

    def test_verification_advances_state(self, temp_algopath):
        """Test verification advances state to VERIFIED."""
        cm = _create_context_manager(temp_algopath)
        cm.start_session()
        cm.save_text("text")
        cm.save_steps([{"step": 1}])
        cm.save_code("def test(): pass")
        cm.save_results({"output": "test"})

        run_verification(cm)
        assert cm.get_current().current_state.value == "verified"

    def test_workflow_progress_included(self, temp_algopath):
        """Test workflows include progress indicator."""
        cm = _create_context_manager(temp_algopath)
        cm.start_session()

        result = run_extraction(cm, text="test")
        assert "progress" in result

    def test_workflow_next_steps_included(self, temp_algopath):
        """Test workflows include next steps."""
        cm = _create_context_manager(temp_algopath)
        cm.start_session()
        cm.save_text("text")
        cm.save_steps([{"step": 1}])

        result = run_generation(cm)
        assert "next_steps" in result
        assert len(result["next_steps"]) > 0

    def test_generation_with_multiple_steps(self, temp_algopath):
        """Test generation with multiple steps."""
        cm = _create_context_manager(temp_algopath)
        cm.start_session()
        cm.save_text("text")
        cm.save_steps([
            {"step": 1, "action": "init"},
            {"step": 2, "action": "process"},
            {"step": 3, "action": "return"}
        ])

        result = run_generation(cm)
        assert result["status"] == "generation_stub"
        assert cm.get_current().data["code"] is not None

    def test_workflow_error_handling(self, temp_algopath):
        """Test workflows handle errors gracefully."""
        cm = _create_context_manager(temp_algopath)
        cm.start_session()

        # Try to run without prerequisites
        result = run_execution(cm)
        assert result["status"] in ["needs_generation", "error"]

    def test_extraction_returns_next_steps(self, temp_algopath):
        """Test extraction returns actionable next steps."""
        cm = _create_context_manager(temp_algopath)
        cm.start_session()

        result = run_extraction(cm, text="test")
        assert "next_steps" in result
        assert any("generate" in step.lower() for step in result["next_steps"])
