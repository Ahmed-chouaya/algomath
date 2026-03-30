"""
End-to-end integration tests for AlgoMath.

Tests complete user workflows from start to finish, including
session resumption and progress tracking.
"""

import pytest
from pathlib import Path

import algomath.context as ctx_module
import algomath.persistence as persist_module
import algomath.state as state_module
from src.context import ContextManager
from src.workflows import run_extraction
from src.intent import detect_intent, IntentType


def _setup_context(temp_dir):
    """Helper to set up ContextManager with temp paths."""
    algopath = Path(temp_dir) / ".algomath"
    persist_module.ALGOMATH_DIR = algopath
    persist_module.ALGORITHMS_DIR = algopath / "algorithms"
    state_module.ALGOMATH_DIR = algopath
    state_module.SESSION_FILE = algopath / "session.json"

    return ctx_module.ContextManager()


class TestEndToEndWorkflow:
    """Test complete user workflows from start to finish."""

    def test_full_extraction_workflow(self, temp_algopath):
        """User extracts algorithm, system persists it."""
        cm = _setup_context(temp_algopath)
        cm.start_session()

        # Step 1: Extract intent
        intent, conf = detect_intent("extract this algorithm")
        assert intent == IntentType.EXTRACT
        assert conf > 0.5

        # Step 2: Run extraction
        result = run_extraction(cm, text="Algorithm: Sort an array")
        assert result["status"] in ["extraction_complete", "stub", "success"]

        # Step 3: Verify persistence
        assert cm.get_current().data["text"] == "Algorithm: Sort an array"

        # Step 4: Check state
        from algomath.state import WorkflowState
        assert cm.get_current().current_state == WorkflowState.TEXT_EXTRACTED

    def test_session_resumption(self, temp_algopath):
        """Simulate interruption and resumption."""
        cm = _setup_context(temp_algopath)
        cm.start_session()

        # User starts work
        cm.save_text("My algorithm", name="my_algo")
        cm.save_steps([{"step": "Initialize"}])

        # Simulate crash - new ContextManager
        cm2 = _setup_context(temp_algopath)
        cm2.start_session()

        # Verify state recovered
        state = cm2.get_current()
        assert state.data["text"] == "My algorithm"
        assert len(state.data["steps"]) == 1

    def test_named_vs_unnamed_algorithms(self, temp_algopath):
        """Test both named (persisted) and unnamed (session-only) algorithms."""
        cm = _setup_context(temp_algopath)
        cm.start_session()

        # Unnamed - session only
        cm.save_text("Unnamed algo")
        assert cm.get_current().current_algorithm is None

        # Named - persisted
        cm.create_algorithm("named_algo")
        cm.save_text("Named algo text")
        assert cm.get_current().current_algorithm == "named_algo"

    def test_progress_indicators(self, temp_algopath):
        """Verify progress display at different states."""
        cm = _setup_context(temp_algopath)
        cm.start_session()

        # Initial state
        progress = cm.get_progress()
        assert progress["progress_percent"] == 0

        # After extraction
        cm.save_text("text")
        progress = cm.get_progress()
        assert progress["progress_percent"] > 0

        # After steps
        cm.save_steps([{"step": 1}])
        progress = cm.get_progress()
        assert progress["progress_percent"] > 25

    def test_complete_workflow_transition(self, temp_algopath):
        """Test full workflow through all states."""
        cm = _setup_context(temp_algopath)
        cm.start_session()

        # IDLE -> TEXT_EXTRACTED
        cm.save_text("algorithm description")
        assert cm.get_current().current_state.value == "text_extracted"

        # TEXT_EXTRACTED -> STEPS_STRUCTURED
        cm.save_steps([{"step": 1}, {"step": 2}])
        assert cm.get_current().current_state.value == "steps_structured"

        # STEPS_STRUCTURED -> CODE_GENERATED
        cm.save_code("def algo(): pass")
        assert cm.get_current().current_state.value == "code_generated"

        # CODE_GENERATED -> EXECUTION_COMPLETE
        cm.save_results({"output": "result"})
        assert cm.get_current().current_state.value == "execution_complete"

        # EXECUTION_COMPLETE -> VERIFIED
        cm.mark_verified()
        assert cm.get_current().current_state.value == "verified"

    def test_algorithm_persistence_and_retrieval(self, temp_algopath):
        """Test saving and loading named algorithms."""
        cm = _setup_context(temp_algopath)
        cm.start_session()

        # Create named algorithm
        cm.create_algorithm("sorting_algorithm")
        cm.save_text("Bubble sort implementation")
        cm.save_steps([{"step": 1}, {"step": 2}])

        # Load in fresh session
        cm2 = _setup_context(temp_algopath)
        cm2.start_session()
        loaded = cm2.load_algorithm("sorting_algorithm")

        assert loaded is not None
        assert loaded.current_algorithm == "sorting_algorithm"
        assert loaded.data["text"] == "Bubble sort implementation"
        assert len(loaded.data["steps"]) == 2

    def test_progress_bar_visual(self, temp_algopath):
        """Test progress bar display format."""
        cm = _setup_context(temp_algopath)
        cm.start_session()

        # Test different widths
        bar = cm.get_progress_bar(width=10)
        assert "█" in bar or "░" in bar
        assert "%" in bar

        # Progress should increase with state
        cm.save_text("text")
        bar1 = cm.get_progress_bar(width=10)
        pct1 = int(bar1.split()[-1].replace('%', ''))

        cm.save_steps([{"step": 1}])
        bar2 = cm.get_progress_bar(width=10)
        pct2 = int(bar2.split()[-1].replace('%', ''))

        assert pct2 > pct1

    def test_data_status_tracking(self, temp_algopath):
        """Test data status reporting."""
        cm = _setup_context(temp_algopath)
        cm.start_session()

        progress = cm.get_progress()
        assert "data_status" in progress
        assert progress["data_status"]["has_text"] is False
        assert progress["data_status"]["has_steps"] is False

        cm.save_text("text")
        progress = cm.get_progress()
        assert progress["data_status"]["has_text"] is True
        assert progress["data_status"]["has_steps"] is False

    def test_intent_routing_with_workflows(self, temp_algopath):
        """Test intent detection routes to correct workflow."""
        from src.intent import route_to_workflow

        cm = _setup_context(temp_algopath)
        cm.start_session()

        # Test extract routing
        intent, _ = detect_intent("extract the algorithm")
        path = route_to_workflow(intent)
        assert path == "src.workflows.extract"

        # Test generate routing
        intent, _ = detect_intent("generate code")
        path = route_to_workflow(intent)
        assert path == "src.workflows.generate"

    def test_multiple_algorithms_listing(self, temp_algopath):
        """Test listing multiple saved algorithms."""
        cm = _setup_context(temp_algopath)
        cm.start_session()

        # Create multiple algorithms
        for i in range(3):
            cm.start_session()  # Fresh session
            cm.create_algorithm(f"algo_{i}")
            cm.save_text(f"Algorithm {i} description")

        algorithms = cm.list_algorithms()
        names = [name for name, _ in algorithms]
        assert "algo_0" in names
        assert "algo_1" in names
        assert "algo_2" in names

    def test_version_tracking(self, temp_algopath):
        """Test algorithm version tracking."""
        cm = _setup_context(temp_algopath)
        cm.start_session()

        cm.create_algorithm("versioned_algo")
        cm.save_text("First version")

        # Save again (should create new version)
        cm.save_steps([{"step": 1}])

        # Check history
        history = cm.get_version_history("versioned_algo")
        assert len(history) >= 1

    def test_workflow_error_recovery(self, temp_algopath):
        """Test error recovery during workflow."""
        cm = _setup_context(temp_algopath)
        cm.start_session()

        # Try to run generation without extraction
        from src.workflows import run_generation
        result = run_generation(cm)
        assert result["status"] in ["needs_extraction", "stub", "error"]
        assert "next_steps" in result
