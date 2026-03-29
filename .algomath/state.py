"""
State management for AlgoMath - tracks workflow state and manages transitions.

This module provides the flexible branching state machine that allows users
to jump between workflow steps and edit at any point.
"""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .persistence import save_algorithm, load_algorithm

ALGOMATH_DIR = Path(".algomath")
SESSION_FILE = ALGOMATH_DIR / "session.json"


class WorkflowState(Enum):
    """Enumeration of all possible workflow states."""
    IDLE = "idle"
    TEXT_EXTRACTED = "text_extracted"
    STEPS_STRUCTURED = "steps_structured"
    CODE_GENERATED = "code_generated"
    EXECUTION_COMPLETE = "execution_complete"
    VERIFIED = "verified"


class SessionState:
    """
    Tracks the current session state and algorithm data.
    
    Supports flexible branching - users can move between states if data exists.
    """
    
    # Define valid transitions (bidirectional for flexibility)
    VALID_TRANSITIONS = {
        WorkflowState.IDLE: [WorkflowState.TEXT_EXTRACTED],
        WorkflowState.TEXT_EXTRACTED: [
            WorkflowState.IDLE, 
            WorkflowState.STEPS_STRUCTURED
        ],
        WorkflowState.STEPS_STRUCTURED: [
            WorkflowState.TEXT_EXTRACTED,
            WorkflowState.CODE_GENERATED
        ],
        WorkflowState.CODE_GENERATED: [
            WorkflowState.STEPS_STRUCTURED,
            WorkflowState.EXECUTION_COMPLETE
        ],
        WorkflowState.EXECUTION_COMPLETE: [
            WorkflowState.CODE_GENERATED,
            WorkflowState.VERIFIED
        ],
        WorkflowState.VERIFIED: [
            WorkflowState.EXECUTION_COMPLETE
        ]
    }
    
    def __init__(self):
        self.current_algorithm: Optional[str] = None
        self.current_state: WorkflowState = WorkflowState.IDLE
        self.data: Dict[str, Any] = {
            "text": None,
            "steps": None,
            "code": None,
            "results": None
        }
        self.created_at: str = datetime.now().isoformat()
        self.updated_at: str = self.created_at
    
    def can_transition_to(self, target: WorkflowState) -> bool:
        """
        Check if transition to target state is valid.
        
        Transitions are valid if:
        - Moving forward: data must exist for the target state
        - Moving backward: always allowed (to edit previous steps)
        """
        if target == self.current_state:
            return True
        
        # Check if transition is in valid transitions list
        if target not in self.VALID_TRANSITIONS.get(self.current_state, []):
            return False
        
        # Moving forward requires data to exist
        state_order = list(WorkflowState)
        current_idx = state_order.index(self.current_state)
        target_idx = state_order.index(target)
        
        if target_idx > current_idx:
            # Moving forward - check if data exists
            return self._has_data_for_state(target)
        
        # Moving backward - always allowed
        return True
    
    def _has_data_for_state(self, state: WorkflowState) -> bool:
        """Check if required data exists for a given state."""
        data_requirements = {
            WorkflowState.TEXT_EXTRACTED: ["text"],
            WorkflowState.STEPS_STRUCTURED: ["steps"],
            WorkflowState.CODE_GENERATED: ["code"],
            WorkflowState.EXECUTION_COMPLETE: ["results"],
            WorkflowState.VERIFIED: ["results"]  # Verification uses results
        }
        
        required_keys = data_requirements.get(state, [])
        return all(self.data.get(k) is not None for k in required_keys)
    
    def transition_to(self, target: WorkflowState) -> bool:
        """Attempt to transition to target state."""
        if not self.can_transition_to(target):
            return False
        
        self.current_state = target
        self.updated_at = datetime.now().isoformat()
        return True
    
    def get_progress(self) -> Dict[str, Any]:
        """Get progress information for display."""
        state_order = list(WorkflowState)
        current_idx = state_order.index(self.current_state)
        total_states = len(state_order) - 1  # Exclude IDLE
        
        progress_pct = (current_idx / total_states * 100) if total_states > 0 else 0
        
        return {
            "current_state": self.current_state.value,
            "algorithm_name": self.current_algorithm,
            "progress_percent": round(progress_pct, 1),
            "steps_completed": current_idx,
            "steps_total": total_states,
            "data_status": {
                "has_text": self.data.get("text") is not None,
                "has_steps": self.data.get("steps") is not None,
                "has_code": self.data.get("code") is not None,
                "has_results": self.data.get("results") is not None
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary."""
        return {
            "current_algorithm": self.current_algorithm,
            "current_state": self.current_state.value,
            "data": self.data,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionState":
        """Deserialize state from dictionary."""
        state = cls()
        state.current_algorithm = data.get("current_algorithm")
        state.current_state = WorkflowState(data.get("current_state", "idle"))
        state.data = data.get("data", {
            "text": None,
            "steps": None,
            "code": None,
            "results": None
        })
        state.created_at = data.get("created_at", datetime.now().isoformat())
        state.updated_at = data.get("updated_at", state.created_at)
        return state


class WorkflowStateManager:
    """Manages workflow state persistence across sessions."""
    
    def __init__(self):
        ALGOMATH_DIR.mkdir(exist_ok=True)
    
    def save_session(self, state: SessionState, persist: bool = True):
        """
        Save session state.
        
        Args:
            state: Current session state
            persist: If True and algorithm is named, also save to algorithm storage
        """
        state.updated_at = datetime.now().isoformat()
        
        # Always save to session file
        session_data = state.to_dict()
        with open(SESSION_FILE, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # If named algorithm, also save to algorithm storage
        if persist and state.current_algorithm:
            algo_data = {
                "name": state.current_algorithm,
                "text": state.data.get("text"),
                "steps": state.data.get("steps"),
                "code": state.data.get("code"),
                "results": state.data.get("results"),
                "current_state": state.current_state.value,
                "updated_at": state.updated_at
            }
            save_algorithm(state.current_algorithm, algo_data)
    
    def load_session(self) -> Optional[SessionState]:
        """Load session state from file."""
        if not SESSION_FILE.exists():
            return None
        
        try:
            with open(SESSION_FILE, 'r') as f:
                data = json.load(f)
            return SessionState.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None
    
    def clear_session(self):
        """Clear session file (for session-only algorithms)."""
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
    
    def load_algorithm_session(self, name: str) -> Optional[SessionState]:
        """Load session state from saved algorithm."""
        algo_data = load_algorithm(name)
        if not algo_data:
            return None
        
        state = SessionState()
        state.current_algorithm = algo_data.get("name")
        state.current_state = WorkflowState(
            algo_data.get("current_state", "idle")
        )
        state.data = {
            "text": algo_data.get("text"),
            "steps": algo_data.get("steps"),
            "code": algo_data.get("code"),
            "results": algo_data.get("results")
        }
        state.created_at = algo_data.get("created_at", datetime.now().isoformat())
        state.updated_at = algo_data.get("updated_at", state.created_at)
        
        return state
