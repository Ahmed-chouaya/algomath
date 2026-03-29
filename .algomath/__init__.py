"""
AlgoMath - A framework for converting mathematical algorithms to executable code.

This package provides the core infrastructure for:
- Storing and versioning algorithms
- Managing workflow state
- Context management across extraction, generation, execution, and verification
"""

from .context import ContextManager
from .state import WorkflowState, SessionState, WorkflowStateManager
from .persistence import (
    AlgorithmStore,
    GitManager,
    save_algorithm,
    load_algorithm,
    list_algorithms,
    delete_algorithm,
    algorithm_exists
)

__all__ = [
    # Main API
    "ContextManager",
    # State management
    "WorkflowState",
    "SessionState",
    "WorkflowStateManager",
    # Persistence
    "AlgorithmStore",
    "GitManager",
    "save_algorithm",
    "load_algorithm",
    "list_algorithms",
    "delete_algorithm",
    "algorithm_exists",
]

__version__ = "0.1.0"
