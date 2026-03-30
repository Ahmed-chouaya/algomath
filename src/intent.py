"""
Intent detection and routing for AlgoMath.

This module provides natural language intent detection and workflow routing,
enabling users to interact with the system using conversational language.
"""

from enum import Enum, auto
from typing import Tuple, List, Dict, Optional
import re


class IntentType(Enum):
    """Enumeration of supported user intents."""
    EXTRACT = auto()   # Extract algorithm from text
    GENERATE = auto()  # Generate code from steps
    RUN = auto()       # Execute generated code
    VERIFY = auto()    # Verify execution results
    STATUS = auto()    # Check current state
    LIST = auto()      # List algorithms
    HELP = auto()      # Show help
    UNKNOWN = auto()   # Could not determine intent


# Keyword mappings for intent detection
INTENT_KEYWORDS: Dict[IntentType, List[str]] = {
    IntentType.EXTRACT: [
        "extract", "parse", "get steps", "analyze text", "pull out",
        "find algorithm", "identify", "get algorithm", "from text",
        "steps from", "parse this", "analyze", "read", "interpret"
    ],
    IntentType.GENERATE: [
        "generate", "create code", "write python", "implement",
        "code this", "make code", "turn into code", "convert to code",
        "python code", "write code", "produce code", "build code"
    ],
    IntentType.RUN: [
        "run", "execute", "execute code", "test", "run code",
        "run it", "execute it", "try it", "run the", "execute the",
        "run algorithm", "execute algorithm", "test code", "try code"
    ],
    IntentType.VERIFY: [
        "verify", "check", "validate", "explain", "confirm",
        "is this correct", "does this work", "validate results",
        "check output", "verify results", "explain why", "how does this work"
    ],
    IntentType.STATUS: [
        "status", "state", "progress", "where am i", "what's next",
        "current state", "show status", "check status", "where are we",
        "what step", "what phase", "how far", "progress so far"
    ],
    IntentType.LIST: [
        "list", "show algorithms", "what do i have", "saved algorithms",
        "my algorithms", "view algorithms", "list algorithms", "show all",
        "what algorithms", "saved", "previous algorithms"
    ],
    IntentType.HELP: [
        "help", "how to", "what can you do", "commands", "how do i",
        "show help", "list commands", "usage", "instructions",
        "what commands", "available commands", "command list"
    ],
}


def _calculate_confidence(user_input: str, keywords: List[str]) -> float:
    """
    Calculate confidence score based on keyword matches.

    Args:
        user_input: The user's input text (lowercased)
        keywords: List of keywords for this intent

    Returns:
        float: Confidence score between 0.0 and 1.0
    """
    if not user_input or not keywords:
        return 0.0

    matches = 0
    matched_phrases = []

    for keyword in keywords:
        if keyword in user_input:
            # Phrase matches get higher weight
            if len(keyword.split()) > 1:
                matches += 2.0
            else:
                matches += 1.0
            matched_phrases.append(keyword)

    if matches == 0:
        return 0.0

    # Confidence based on number of matches relative to keyword list
    # and weighted by phrase matches
    base_confidence = matches / (len(keywords) * 0.3)

    # Boost confidence for direct phrase matches
    if any(phrase in user_input for phrase in matched_phrases if len(phrase.split()) > 1):
        base_confidence = min(base_confidence * 1.3, 1.0)

    return min(base_confidence, 1.0)


def detect_intent(user_input: str) -> Tuple[IntentType, float]:
    """
    Detect user intent from natural language input.

    Uses keyword matching to classify the user's intent and returns
    both the intent type and a confidence score.

    Args:
        user_input: The natural language input from the user

    Returns:
        Tuple of (IntentType, confidence_score)
        confidence_score is between 0.0 and 1.0

    Examples:
        >>> detect_intent("extract the algorithm from this text")
        (IntentType.EXTRACT, 0.85)

        >>> detect_intent("generate code for this")
        (IntentType.GENERATE, 0.92)

        >>> detect_intent("run it")
        (IntentType.RUN, 0.45)  # Low confidence - needs context

        >>> detect_intent("can you help me")
        (IntentType.HELP, 0.90)
    """
    if not user_input or not isinstance(user_input, str):
        return IntentType.UNKNOWN, 0.0

    normalized = user_input.lower().strip()

    # Remove punctuation for matching
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()

    scores: Dict[IntentType, float] = {}

    for intent_type, keywords in INTENT_KEYWORDS.items():
        if intent_type == IntentType.UNKNOWN:
            continue
        scores[intent_type] = _calculate_confidence(normalized, keywords)

    # Find highest scoring intent
    if not scores:
        return IntentType.UNKNOWN, 0.0

    best_intent = max(scores, key=scores.get)
    best_score = scores[best_intent]

    # Check for ambiguity (multiple high scores)
    high_scores = [s for s in scores.values() if s > 0.5]
    if len(high_scores) > 1:
        # Reduce confidence if multiple intents match
        best_score *= 0.8

    # Unknown if below threshold
    if best_score < 0.2:
        return IntentType.UNKNOWN, best_score

    return best_intent, round(best_score, 2)


def route_to_workflow(intent: IntentType) -> Optional[str]:
    """
    Return the workflow module path for the given intent.

    Maps detected intents to their corresponding workflow modules.

    Args:
        intent: The detected intent type

    Returns:
        Module path string or None if no workflow exists

    Examples:
        >>> route_to_workflow(IntentType.EXTRACT)
        'src.workflows.extract'

        >>> route_to_workflow(IntentType.UNKNOWN)
        None
    """
    workflow_map: Dict[IntentType, Optional[str]] = {
        IntentType.EXTRACT: 'src.workflows.extract',
        IntentType.GENERATE: 'src.workflows.generate',
        IntentType.RUN: 'src.workflows.run',
        IntentType.VERIFY: 'src.workflows.verify',
        IntentType.STATUS: None,  # Handled by context directly
        IntentType.LIST: None,    # Handled by context directly
        IntentType.HELP: None,    # Handled by command system
        IntentType.UNKNOWN: None,
    }

    return workflow_map.get(intent)


def suggest_next_steps(current_state: str) -> List[str]:
    """
    Suggest next actions based on current workflow state.

    Provides context-aware recommendations for what the user can do next.

    Args:
        current_state: Current state identifier (e.g., 'TEXT_EXTRACTED',
                      'CODE_GENERATED', 'EXECUTION_COMPLETE', etc.)

    Returns:
        List of actionable suggestions

    Examples:
        >>> suggest_next_steps('TEXT_EXTRACTED')
        ['Generate code with /algo-generate', 'Edit extracted text', 'Start over with /algo-extract']

        >>> suggest_next_steps('CODE_GENERATED')
        ['Run the code with /algo-run', 'Review code before running', 'Regenerate if needed']

        >>> suggest_next_steps('EXECUTION_COMPLETE')
        ['Verify results with /algo-verify', 'Run with different inputs', 'Modify and regenerate']
    """
    if not current_state:
        return [
            "Extract an algorithm with /algo-extract",
            "List saved algorithms with /algo-list",
            "Show help with /algo-help"
        ]

    suggestions: Dict[str, List[str]] = {
        'NO_SESSION': [
            "Start by extracting an algorithm: /algo-extract",
            "Or load a saved algorithm: /algo-extract [name]",
            "See all commands: /algo-help"
        ],
        'TEXT_SAVED': [
            "Extract steps from the text: /algo-extract (auto-detects)",
            "View current text: /algo-status",
            "Start over: /algo-extract"
        ],
        'TEXT_EXTRACTED': [
            "Generate code with /algo-generate",
            "Review extracted steps: /algo-status",
            "Edit the algorithm text",
            "Extract a different algorithm: /algo-extract"
        ],
        'STEPS_STRUCTURED': [
            "Generate Python code: /algo-generate",
            "Review structured steps: /algo-status",
            "Go back and edit: /algo-extract",
            "View all saved: /algo-list"
        ],
        'CODE_GENERATED': [
            "Run the code: /algo-run",
            "Review code before running: /algo-verify",
            "Regenerate if needed: /algo-generate",
            "Check current status: /algo-status"
        ],
        'CODE_SAVED': [
            "Execute the code: /algo-run",
            "Run with specific input: /algo-run [input]",
            "Review the code: /algo-status"
        ],
        'EXECUTION_COMPLETE': [
            "Verify results: /algo-verify",
            "Run with different inputs: /algo-run",
            "Check execution details: /algo-status",
            "Start new algorithm: /algo-extract"
        ],
        'EXECUTION_FAILED': [
            "Review the error: /algo-status",
            "Regenerate code: /algo-generate",
            "Check inputs and try again: /algo-run",
            "Verify code logic: /algo-verify"
        ],
        'VERIFICATION_COMPLETE': [
            "Extract another algorithm: /algo-extract",
            "List all saved algorithms: /algo-list",
            "Start fresh: /algo-extract"
        ],
        'DEFAULT': [
            "Check current status: /algo-status",
            "Show available commands: /algo-help",
            "List saved algorithms: /algo-list"
        ]
    }

    return suggestions.get(current_state, suggestions['DEFAULT'])


def get_intent_description(intent: IntentType) -> str:
    """
    Get a human-readable description of an intent type.

    Args:
        intent: The intent type

    Returns:
        Description string
    """
    descriptions: Dict[IntentType, str] = {
        IntentType.EXTRACT: "Extract algorithm from mathematical text",
        IntentType.GENERATE: "Generate executable code from algorithm steps",
        IntentType.RUN: "Execute generated code",
        IntentType.VERIFY: "Verify execution results and explain behavior",
        IntentType.STATUS: "Show current algorithm state and progress",
        IntentType.LIST: "List all saved algorithms",
        IntentType.HELP: "Show help and available commands",
        IntentType.UNKNOWN: "Unknown intent - could not determine",
    }
    return descriptions.get(intent, "Unknown")


# Exports
__all__ = [
    'IntentType',
    'detect_intent',
    'route_to_workflow',
    'suggest_next_steps',
    'get_intent_description',
    'INTENT_KEYWORDS',
]
