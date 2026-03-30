"""
Unit tests for ContextManager.

Tests the main interface for managing AlgoMath workflows, including
session management, state transitions, and progress tracking.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

# Import after path setup in conftest
import algomath.context as ctx_module
import algomath.persistence as persist_module
import algomath.state as state_module
from algomath.state import WorkflowState


def _create_context_manager(temp_dir):
    """Helper to create a ContextManager with temp paths."""
    # Patch paths
    algopath = Path(temp_dir) / ".algomath"
    persist_module.ALGOMATH_DIR = algopath
    persist_module.ALGORITHMS_DIR = algopath / "algorithms"
    state_module.ALGOMATH_DIR = algopath
    state_module.SESSION_FILE = algopath / "session.json"

    return ctx_module.ContextManager()


class TestContextManager:
    """Test suite for ContextManager functionality."""

    def test_start_session(self, temp_algopath):
        """Test session initialization."""
        cm = _create_context_manager(temp_algopath)

        cm.start_session()
        state = cm.get_current()
        assert state.current_state == WorkflowState.IDLE
        assert state.current_algorithm is None

    def test_save_text_transitions_state(self, temp_algopath):
        """Test that saving text advances state."""
        cm = _create_context_manager(temp_algopath)

        cm.start_session()
        cm.save_text("test algorithm", name="test_algo")
        state = cm.get_current()
        assert state.current_state == WorkflowState.TEXT_EXTRACTED
        assert state.current_algorithm == "test_algo"

    def test_state_transitions(self, temp_algopath):
        """Test complete state transition flow."""
        cm = _create_context_manager(temp_algopath)

        cm.start_session()

        # IDLE -> TEXT_EXTRACTED
        cm.save_text("text")
        assert cm.get_current().current_state == WorkflowState.TEXT_EXTRACTED

        # TEXT_EXTRACTED -> STEPS_STRUCTURED
        cm.save_steps([{"step": 1}])
        assert cm.get_current().current_state == WorkflowState.STEPS_STRUCTURED

        # STEPS_STRUCTURED -> CODE_GENERATED
        cm.save_code("def algo(): pass")
        assert cm.get_current().current_state == WorkflowState.CODE_GENERATED

    def test_session_persistence(self, temp_algopath):
        """Test that session persists across ContextManager instances."""
        cm = _create_context_manager(temp_algopath)

        cm.start_session()
        cm.save_text("persistent text")

        # Simulate new session
        cm2 = _create_context_manager(temp_algopath)
        cm2.start_session()

        # Verify state recovered
        state = cm2.get_current()
        assert state.data.get("text") == "persistent text"

    def test_get_progress(self, temp_algopath):
        """Test progress reporting."""
        cm = _create_context_manager(temp_algopath)

        cm.start_session()
        progress = cm.get_progress()
        assert "current_state" in progress
        assert "progress_percent" in progress
        assert progress["current_state"] == "idle"
        assert progress["progress_percent"] == 0.0

    def test_create_algorithm(self, temp_algopath):
        """Test creating a named algorithm."""
        cm = _create_context_manager(temp_algopath)

        cm.start_session()
        result = cm.create_algorithm("my_algo")
        assert result is True
        assert cm.get_current().current_algorithm == "my_algo"

    def test_create_duplicate_algorithm(self, temp_algopath):
        """Test creating duplicate algorithm name fails."""
        cm = _create_context_manager(temp_algopath)

        cm.start_session()
        cm.create_algorithm("my_algo")

        # Try to create again
        result = cm.create_algorithm("my_algo")
        assert result is False

    def test_save_steps_advances_state(self, temp_algopath):
        """Test that saving steps advances state."""
        cm = _create_context_manager(temp_algopath)

        cm.start_session()
        cm.save_text("text")
        result = cm.save_steps([{"step": 1, "action": "init"}])

        assert result is True
        assert cm.get_current().current_state == WorkflowState.STEPS_STRUCTURED
        assert cm.get_current().data["steps"] == [{"step": 1, "action": "init"}]

    def test_save_code_advances_state(self, temp_algopath):
        """Test that saving code advances state."""
        cm = _create_context_manager(temp_algopath)

        cm.start_session()
        cm.save_text("text")
        cm.save_steps([{"step": 1}])
        result = cm.save_code("def test(): pass")

        assert result is True
        assert cm.get_current().current_state == WorkflowState.CODE_GENERATED
        assert "code" in cm.get_current().data

    def test_save_results_advances_state(self, temp_algopath):
        """Test that saving results advances state."""
        cm = _create_context_manager(temp_algopath)

        cm.start_session()
        cm.save_text("text")
        cm.save_steps([{"step": 1}])
        cm.save_code("def test(): pass")
        result = cm.save_results({"output": "test"})

        assert result is True
        assert cm.get_current().current_state == WorkflowState.EXECUTION_COMPLETE
        assert "results" in cm.get_current().data

    def test_mark_verified_advances_state(self, temp_algopath):
        """Test marking as verified."""
        cm = _create_context_manager(temp_algopath)

        cm.start_session()
        cm.save_text("text")
        cm.save_steps([{"step": 1}])
        cm.save_code("def test(): pass")
        cm.save_results({"output": "test"})
        result = cm.mark_verified()

        assert result is True
        assert cm.get_current().current_state == WorkflowState.VERIFIED

    def test_progress_bar_format(self, temp_algopath):
        """Test progress bar format."""
        cm = _create_context_manager(temp_algopath)

        cm.start_session()
        bar = cm.get_progress_bar(width=10)
        assert "░" in bar or "█" in bar
        assert "%" in bar

    def test_can_transition_to(self, temp_algopath):
        """Test transition checking."""
        cm = _create_context_manager(temp_algopath)

        cm.start_session()
        cm.save_text("text")

        # Can transition forward with data
        assert cm.can_transition_to("steps_structured") is True

        # Can always go back
        assert cm.can_transition_to("text_extracted") is True

        # Cannot transition to invalid state
        assert cm.can_transition_to("invalid_state") is False

    def test_session_without_start_raises(self, temp_algopath):
        """Test that accessing current without starting session raises."""
        cm = _create_context_manager(temp_algopath)

        with pytest.raises(RuntimeError, match="Session not started"):
            cm.get_current()

    def test_load_algorithm(self, temp_algopath):
        """Test loading a saved algorithm."""
        cm = _create_context_manager(temp_algopath)

        cm.start_session()
        cm.create_algorithm("test_algo")
        cm.save_text("algorithm text")
        cm.save_steps([{"step": 1}])

        # Create new manager and load
        cm2 = _create_context_manager(temp_algopath)

        loaded = cm2.load_algorithm("test_algo")
        assert loaded is not None
        assert loaded.current_algorithm == "test_algo"
        assert loaded.data["text"] == "algorithm text"

    def test_list_algorithms(self, temp_algopath):
        """Test listing algorithms."""
        cm = _create_context_manager(temp_algopath)

        cm.start_session()
        cm.create_algorithm("algo1")
        cm.save_text("text1")

        cm.start_session()
        cm.create_algorithm("algo2")
        cm.save_text("text2")

        algorithms = cm.list_algorithms()
        names = [name for name, _ in algorithms]
        assert "algo1" in names
        assert "algo2" in names

    def test_delete_algorithm(self, temp_algopath):
        """Test deleting an algorithm."""
        cm = _create_context_manager(temp_algopath)

        cm.start_session()
        cm.create_algorithm("to_delete")
        cm.save_text("delete me")

        # Delete
        result = cm.delete_algorithm("to_delete")
        assert result is True

        # Verify deleted
        algorithms = cm.list_algorithms()
        names = [name for name, _ in algorithms]
        assert "to_delete" not in names
