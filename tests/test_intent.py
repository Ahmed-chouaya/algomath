"""
Unit tests for intent detection.

Tests the natural language intent detection and routing system.
"""

import pytest
from src.intent import detect_intent, IntentType, route_to_workflow, suggest_next_steps


class TestIntentDetection:
    """Test suite for intent detection."""

    def test_extract_keywords(self):
        """Test extraction intent detection."""
        inputs = [
            "extract the algorithm",
            "parse this text",
            "get steps from this",
            "analyze this algorithm"
        ]
        for inp in inputs:
            intent, conf = detect_intent(inp)
            assert intent == IntentType.EXTRACT, f"Failed for: {inp}"
            assert conf > 0.5, f"Low confidence for: {inp}"

    def test_generate_keywords(self):
        """Test generation intent detection."""
        inputs = [
            "generate code",
            "create python code",
            "write the implementation"
        ]
        for inp in inputs:
            intent, conf = detect_intent(inp)
            assert intent == IntentType.GENERATE, f"Failed for: {inp}"
            assert conf > 0.5, f"Low confidence for: {inp}"

    def test_run_keywords(self):
        """Test execution intent detection."""
        inputs = [
            "run the code",
            "execute this",
            "test the algorithm"
        ]
        for inp in inputs:
            intent, conf = detect_intent(inp)
            assert intent == IntentType.RUN, f"Failed for: {inp}"
            assert conf > 0.5, f"Low confidence for: {inp}"

    def test_verify_keywords(self):
        """Test verification intent detection."""
        inputs = [
            "verify results",
            "check output",
            "validate this"
        ]
        for inp in inputs:
            intent, conf = detect_intent(inp)
            assert intent == IntentType.VERIFY, f"Failed for: {inp}"
            assert conf > 0.5, f"Low confidence for: {inp}"

    def test_status_keywords(self):
        """Test status intent detection."""
        inputs = [
            "what's my status",
            "show progress",
            "where am i"
        ]
        for inp in inputs:
            intent, conf = detect_intent(inp)
            assert intent == IntentType.STATUS, f"Failed for: {inp}"
            assert conf > 0.5, f"Low confidence for: {inp}"

    def test_list_keywords(self):
        """Test list intent detection."""
        intent, conf = detect_intent("show me my algorithms")
        assert intent == IntentType.LIST
        assert conf > 0.5

    def test_help_keywords(self):
        """Test help intent detection."""
        intent, conf = detect_intent("how do I use this")
        assert intent == IntentType.HELP
        assert conf > 0.5

    def test_unknown_input(self):
        """Test unknown intent detection."""
        intent, conf = detect_intent("random unrelated text")
        assert intent == IntentType.UNKNOWN
        assert conf < 0.5

    def test_confidence_calculation(self):
        """Test confidence varies by input specificity."""
        # Single keyword should have lower confidence than multiple
        _, conf1 = detect_intent("extract")
        _, conf2 = detect_intent("extract the algorithm from this text")
        assert conf2 > conf1

    def test_empty_input(self):
        """Test empty input handling."""
        intent, conf = detect_intent("")
        assert intent == IntentType.UNKNOWN
        assert conf == 0.0

    def test_whitespace_input(self):
        """Test whitespace-only input."""
        intent, conf = detect_intent("   ")
        assert intent == IntentType.UNKNOWN
        assert conf == 0.0

    def test_case_insensitivity(self):
        """Test case-insensitive matching."""
        intent1, conf1 = detect_intent("EXTRACT THE ALGORITHM")
        intent2, conf2 = detect_intent("extract the algorithm")
        assert intent1 == intent2
        assert conf1 == conf2

    def test_punctuation_handling(self):
        """Test input with punctuation."""
        intent, conf = detect_intent("extract the algorithm! (please)")
        assert intent == IntentType.EXTRACT
        assert conf > 0.5


class TestRouteToWorkflow:
    """Test suite for workflow routing."""

    def test_extract_routing(self):
        """Test EXTRACT intent routing."""
        path = route_to_workflow(IntentType.EXTRACT)
        assert path == "src.workflows.extract"

    def test_generate_routing(self):
        """Test GENERATE intent routing."""
        path = route_to_workflow(IntentType.GENERATE)
        assert path == "src.workflows.generate"

    def test_run_routing(self):
        """Test RUN intent routing."""
        path = route_to_workflow(IntentType.RUN)
        assert path == "src.workflows.run"

    def test_verify_routing(self):
        """Test VERIFY intent routing."""
        path = route_to_workflow(IntentType.VERIFY)
        assert path == "src.workflows.verify"

    def test_status_routing(self):
        """Test STATUS intent routing."""
        path = route_to_workflow(IntentType.STATUS)
        assert path is None  # Handled by context directly

    def test_list_routing(self):
        """Test LIST intent routing."""
        path = route_to_workflow(IntentType.LIST)
        assert path is None  # Handled by context directly

    def test_help_routing(self):
        """Test HELP intent routing."""
        path = route_to_workflow(IntentType.HELP)
        assert path is None  # Handled by command system

    def test_unknown_routing(self):
        """Test UNKNOWN intent routing."""
        path = route_to_workflow(IntentType.UNKNOWN)
        assert path is None


class TestSuggestNextSteps:
    """Test suite for next step suggestions."""

    def test_text_extracted_suggestions(self):
        """Test suggestions after text extraction."""
        suggestions = suggest_next_steps('TEXT_EXTRACTED')
        assert len(suggestions) > 0
        assert any('generate' in s.lower() for s in suggestions)

    def test_steps_structured_suggestions(self):
        """Test suggestions after steps structured."""
        suggestions = suggest_next_steps('STEPS_STRUCTURED')
        assert len(suggestions) > 0
        assert any('code' in s.lower() or 'generate' in s.lower() for s in suggestions)

    def test_code_generated_suggestions(self):
        """Test suggestions after code generation."""
        suggestions = suggest_next_steps('CODE_GENERATED')
        assert len(suggestions) > 0
        assert any('run' in s.lower() or 'execute' in s.lower() for s in suggestions)

    def test_execution_complete_suggestions(self):
        """Test suggestions after execution."""
        suggestions = suggest_next_steps('EXECUTION_COMPLETE')
        assert len(suggestions) > 0
        assert any('verify' in s.lower() for s in suggestions)

    def test_default_suggestions(self):
        """Test default suggestions."""
        suggestions = suggest_next_steps('UNKNOWN_STATE')
        assert len(suggestions) > 0
        assert any('help' in s.lower() or 'status' in s.lower() for s in suggestions)

    def test_empty_state_suggestions(self):
        """Test suggestions for empty state."""
        suggestions = suggest_next_steps('')
        assert len(suggestions) > 0
        assert any('extract' in s.lower() for s in suggestions)
