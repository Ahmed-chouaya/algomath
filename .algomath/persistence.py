"""
Persistence layer for AlgoMath - handles algorithm storage and git versioning.

This module provides file-based persistence with automatic git versioning.
All operations are automatic - users don't need git knowledge.
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

ALGOMATH_DIR = Path(".algomath")
ALGORITHMS_DIR = ALGOMATH_DIR / "algorithms"


class GitManager:
    """Handles automatic git versioning for algorithms."""
    
    def __init__(self, repo_path: Path = ALGOMATH_DIR):
        self.repo_path = repo_path
        self._ensure_repo()
    
    def _ensure_repo(self):
        """Initialize git repo if it doesn't exist."""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            subprocess.run(
                ["git", "init"],
                cwd=self.repo_path,
                capture_output=True,
                check=True
            )
            # Create initial commit
            subprocess.run(
                ["git", "config", "user.email", "algomath@local"],
                cwd=self.repo_path,
                capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.name", "AlgoMath"],
                cwd=self.repo_path,
                capture_output=True
            )
    
    def commit_algorithm(self, name: str, message: Optional[str] = None) -> str:
        """Commit algorithm changes and return commit hash."""
        if message is None:
            message = f"update({name}): algorithm changes"
        
        algorithm_dir = ALGORITHMS_DIR / name
        
        # Stage all changes
        subprocess.run(
            ["git", "add", "."],
            cwd=self.repo_path,
            capture_output=True
        )
        
        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=self.repo_path,
            capture_output=True
        )
        
        # Get commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        return result.stdout.strip()
    
    def get_version(self, name: str) -> Optional[str]:
        """Get current commit hash for algorithm."""
        algorithm_dir = ALGORITHMS_DIR / name
        if not algorithm_dir.exists():
            return None
        
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        return result.stdout.strip() if result.returncode == 0 else None
    
    def get_history(self, name: str) -> List[Dict]:
        """Get commit history for algorithm."""
        algorithm_dir = ALGORITHMS_DIR / name
        if not algorithm_dir.exists():
            return []
        
        result = subprocess.run(
            ["git", "log", "--format=%H|%s|%ai", "--", f"algorithms/{name}/"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        history = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) >= 3:
                    history.append({
                        "hash": parts[0],
                        "message": parts[1],
                        "date": parts[2]
                    })
        
        return history
    
    def checkout_version(self, name: str, commit_hash: str) -> bool:
        """Restore algorithm to specific version."""
        algorithm_dir = ALGORITHMS_DIR / name
        if not algorithm_dir.exists():
            return False
        
        result = subprocess.run(
            ["git", "checkout", commit_hash, "--", f"algorithms/{name}/"],
            cwd=self.repo_path,
            capture_output=True
        )
        
        return result.returncode == 0


class AlgorithmStore:
    """Manages algorithm storage with automatic versioning."""
    
    def __init__(self):
        self._ensure_dirs()
        self.git = GitManager()
    
    def _ensure_dirs(self):
        """Ensure storage directories exist."""
        ALGOMATH_DIR.mkdir(exist_ok=True)
        ALGORITHMS_DIR.mkdir(exist_ok=True)
    
    def save_algorithm(self, name: str, data: Dict) -> str:
        """
        Save algorithm data to storage.
        
        Returns:
            commit_hash: The git commit hash of this version
        """
        algorithm_dir = ALGORITHMS_DIR / name
        algorithm_dir.mkdir(exist_ok=True)
        
        # Add metadata
        data["name"] = name
        data["updated_at"] = datetime.now().isoformat()
        
        if "created_at" not in data:
            data["created_at"] = data["updated_at"]
        
        # Save to file
        algo_file = algorithm_dir / "algorithm.json"
        with open(algo_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Auto-commit
        commit_hash = self.git.commit_algorithm(
            name, 
            f"update({name}): save algorithm data"
        )
        data["version"] = commit_hash
        
        # Update file with version
        with open(algo_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return commit_hash
    
    def load_algorithm(self, name: str) -> Optional[Dict]:
        """Load algorithm data from storage."""
        algorithm_dir = ALGORITHMS_DIR / name
        algo_file = algorithm_dir / "algorithm.json"
        
        if not algo_file.exists():
            return None
        
        with open(algo_file, 'r') as f:
            data = json.load(f)
        
        # Add current version
        data["version"] = self.git.get_version(name)
        
        return data
    
    def list_algorithms(self) -> List[str]:
        """Return list of all saved algorithm names."""
        if not ALGORITHMS_DIR.exists():
            return []
        
        return [
            d.name for d in ALGORITHMS_DIR.iterdir() 
            if d.is_dir() and (d / "algorithm.json").exists()
        ]
    
    def delete_algorithm(self, name: str) -> bool:
        """Remove algorithm from storage."""
        algorithm_dir = ALGORITHMS_DIR / name
        
        if not algorithm_dir.exists():
            return False
        
        import shutil
        shutil.rmtree(algorithm_dir)
        
        # Commit the deletion
        self.git.commit_algorithm(name, f"delete({name}): removed algorithm")
        
        return True
    
    def algorithm_exists(self, name: str) -> bool:
        """Check if algorithm exists in storage."""
        algorithm_dir = ALGORITHMS_DIR / name
        return (algorithm_dir / "algorithm.json").exists()


# Convenience functions
_store = None

def _get_store() -> AlgorithmStore:
    """Get or create singleton store instance."""
    global _store
    if _store is None:
        _store = AlgorithmStore()
    return _store


def save_algorithm(name: str, data: Dict) -> str:
    """Save algorithm with automatic versioning."""
    return _get_store().save_algorithm(name, data)


def load_algorithm(name: str) -> Optional[Dict]:
    """Load algorithm by name."""
    return _get_store().load_algorithm(name)


def list_algorithms() -> List[str]:
    """List all saved algorithms."""
    return _get_store().list_algorithms()


def delete_algorithm(name: str) -> bool:
    """Delete algorithm by name."""
    return _get_store().delete_algorithm(name)


def algorithm_exists(name: str) -> bool:
    """Check if algorithm exists."""
    return _get_store().algorithm_exists(name)
