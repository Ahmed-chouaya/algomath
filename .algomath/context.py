"""
Context Manager for AlgoMath - the main interface for workflow state management.

This module provides the ContextManager class that orchestrates the entire workflow:
- Starting and resuming sessions
- Managing algorithm data and state transitions
- Handling both named (persistent) and session-only (unnamed) algorithms
- Providing progress reporting
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .persistence import (
    AlgorithmStore,
    save_algorithm,
    load_algorithm,
    list_algorithms,
    delete_algorithm,
    algorithm_exists,
    GitManager
)
from .state import (
    WorkflowState,
    SessionState,
    WorkflowStateManager
)


class ContextManager:
    """
    Main interface for managing AlgoMath workflows.
    
    This class coordinates between persistence and state management to provide
    a unified API for the workflow engine.
    """
    
    def __init__(self):
        self.store = AlgorithmStore()
        self.state_manager = WorkflowStateManager()
        self._current_state: Optional[SessionState] = None
    
    def start_session(self) -> SessionState:
        """
        Start a new session or resume existing one.
        
        Returns:
            SessionState: Current session state
        """
        # Try to load existing session
        existing_state = self.state_manager.load_session()
        
        if existing_state:
            self._current_state = existing_state
        else:
            # Create new session
            self._current_state = SessionState()
            self.state_manager.save_session(self._current_state, persist=False)
        
        return self._current_state
    
    def get_current(self) -> SessionState:
        """
        Get current session state.
        
        Raises:
            RuntimeError: If start_session() hasn't been called
        """
        if self._current_state is None:
            raise RuntimeError("Session not started. Call start_session() first.")
        return self._current_state
    
    def create_algorithm(self, name: str) -> bool:
        """
        Create a new named algorithm.
        
        Args:
            name: Algorithm name
            
        Returns:
            bool: True if created, False if name already exists
        """
        if algorithm_exists(name):
            return False
        
        # Set up new state with name
        state = SessionState()
        state.current_algorithm = name
        self._current_state = state
        
        # Save
        self.state_manager.save_session(state, persist=True)
        return True
    
    def load_algorithm(self, name: str) -> Optional[SessionState]:
        """
        Load an existing algorithm by name.
        
        Args:
            name: Algorithm name
            
        Returns:
            SessionState if found, None otherwise
        """
        state = self.state_manager.load_algorithm_session(name)
        if state:
            self._current_state = state
            # Also save to session for resumption
            self.state_manager.save_session(state, persist=False)
        return state
    
    def save_text(self, text: str, name: Optional[str] = None) -> bool:
        """
        Save extracted text and advance state.
        
        Args:
            text: Mathematical text describing algorithm
            name: Optional name (if not already set)
            
        Returns:
            bool: True if state advanced successfully
        """
        state = self.get_current()
        
        # Set name if provided
        if name and not state.current_algorithm:
            state.current_algorithm = name
        
        # Save data
        state.data["text"] = text
        
        # Advance state
        success = state.transition_to(WorkflowState.TEXT_EXTRACTED)
        
        # Persist
        self.state_manager.save_session(
            state, 
            persist=state.current_algorithm is not None
        )
        
        return success
    
    def save_steps(self, steps: List[Dict[str, Any]]) -> bool:
        """
        Save structured algorithm steps and advance state.
        
        Args:
            steps: List of algorithm steps (JSON format)
            
        Returns:
            bool: True if state advanced successfully
        """
        state = self.get_current()
        
        # Save data
        state.data["steps"] = steps
        
        # Advance state
        success = state.transition_to(WorkflowState.STEPS_STRUCTURED)
        
        # Persist
        self.state_manager.save_session(
            state,
            persist=state.current_algorithm is not None
        )
        
        return success
    
    def save_code(self, code: str) -> bool:
        """
        Save generated code and advance state.
        
        Args:
            code: Generated Python code
            
        Returns:
            bool: True if state advanced successfully
        """
        state = self.get_current()
        
        # Save data
        state.data["code"] = code
        
        # Advance state
        success = state.transition_to(WorkflowState.CODE_GENERATED)
        
        # Persist
        self.state_manager.save_session(
            state,
            persist=state.current_algorithm is not None
        )
        
        return success
    
    def save_results(self, results: Dict[str, Any]) -> bool:
        """
        Save execution results and advance state.
        
        Args:
            results: Execution output (stdout, stderr, status, etc.)
            
        Returns:
            bool: True if state advanced successfully
        """
        state = self.get_current()
        
        # Save data
        state.data["results"] = results
        
        # Advance state
        success = state.transition_to(WorkflowState.EXECUTION_COMPLETE)
        
        # Persist
        self.state_manager.save_session(
            state,
            persist=state.current_algorithm is not None
        )
        
        return success
    
    def mark_verified(self) -> bool:
        """
        Mark algorithm as verified.
        
        Returns:
            bool: True if state advanced successfully
        """
        state = self.get_current()
        
        # Advance state
        success = state.transition_to(WorkflowState.VERIFIED)
        
        # Persist
        self.state_manager.save_session(
            state,
            persist=state.current_algorithm is not None
        )
        
        return success
    
    def get_progress(self) -> Dict[str, Any]:
        """
        Get progress information for display.
        
        Returns:
            Dict with progress information including:
            - current_state: Current workflow state
            - algorithm_name: Name or "(unnamed)"
            - progress_percent: Percentage complete (0-100)
            - steps_completed: Number of steps done
            - steps_total: Total number of steps
            - data_status: Which data exists
        """
        state = self.get_current()
        progress = state.get_progress()
        
        # Enhance with name display
        progress["algorithm_name"] = (
            state.current_algorithm 
            if state.current_algorithm 
            else "(unnamed)"
        )
        
        return progress
    
    def get_progress_bar(self, width: int = 40) -> str:
        """
        Get a visual progress bar string.
        
        Args:
            width: Width of progress bar in characters
            
        Returns:
            Formatted progress bar string
        """
        progress = self.get_progress()
        pct = progress["progress_percent"]
        filled = int(width * pct / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"{bar} {pct}%"
    
    def list_algorithms(self) -> List[Tuple[str, str]]:
        """
        Get list of all saved algorithms.
        
        Returns:
            List of (name, last_updated) tuples
        """
        from .persistence import ALGORITHMS_DIR
        import json
        
        algorithms = []
        if ALGORITHMS_DIR.exists():
            for algo_dir in ALGORITHMS_DIR.iterdir():
                if algo_dir.is_dir():
                    algo_file = algo_dir / "algorithm.json"
                    if algo_file.exists():
                        try:
                            with open(algo_file, 'r') as f:
                                data = json.load(f)
                                updated = data.get("updated_at", "unknown")
                                algorithms.append((algo_dir.name, updated))
                        except (json.JSONDecodeError, IOError):
                            pass
        
        return sorted(algorithms, key=lambda x: x[1], reverse=True)
    
    def can_transition_to(self, state_name: str) -> bool:
        """
        Check if transition to a state is valid.
        
        Args:
            state_name: Target state (e.g., "code_generated")
            
        Returns:
            bool: True if transition is valid
        """
        try:
            target = WorkflowState(state_name)
        except ValueError:
            return False
        
        return self.get_current().can_transition_to(target)
    
    def delete_algorithm(self, name: str) -> bool:
        """
        Delete a saved algorithm.
        
        Args:
            name: Algorithm name
            
        Returns:
            bool: True if deleted
        """
        return delete_algorithm(name)
    
    def get_version_history(self, name: str) -> List[Dict[str, Any]]:
        """
        Get version history for an algorithm.
        
        Args:
            name: Algorithm name
            
        Returns:
            List of version records
        """
        git = GitManager()
        return git.get_history(name)
    
    def checkout_version(self, name: str, commit_hash: str) -> bool:
        """
        Restore algorithm to a specific version.
        
        Args:
            name: Algorithm name
            commit_hash: Version to restore
            
        Returns:
            bool: True if successful
        """
        git = GitManager()
        return git.checkout_version(name, commit_hash)
    
    def get_current_version(self, name: str) -> Optional[str]:
        """
        Get current version hash for algorithm.
        
        Args:
            name: Algorithm name
            
        Returns:
            Commit hash or None
        """
        git = GitManager()
        return git.get_version(name)
