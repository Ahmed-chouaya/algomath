"""
Unit tests for persistence layer.

Tests algorithm storage, git versioning, and file operations.
"""

import pytest
import json
from pathlib import Path
import tempfile
import shutil
import subprocess

import algomath.persistence as persist_module
from algomath.persistence import AlgorithmStore, GitManager


def _setup_persistence_paths(temp_dir):
    """Helper to set up temp paths for persistence module."""
    algopath = Path(temp_dir) / ".algomath"
    persist_module.ALGOMATH_DIR = algopath
    persist_module.ALGORITHMS_DIR = algopath / "algorithms"


class TestAlgorithmStore:
    """Test suite for AlgorithmStore."""

    def test_save_and_load(self, temp_algopath):
        """Test saving and loading algorithm data."""
        _setup_persistence_paths(temp_algopath)
        store = AlgorithmStore()

        data = {
            "name": "test",
            "text": "algorithm text",
            "steps": [{"type": "loop"}],
            "code": "def test(): pass"
        }
        commit_hash = store.save_algorithm("test", data)
        assert len(commit_hash) == 40  # SHA-1 hash

        loaded = store.load_algorithm("test")
        assert loaded["text"] == "algorithm text"
        assert loaded["steps"] == [{"type": "loop"}]

    def test_list_algorithms(self, temp_algopath):
        """Test listing saved algorithms."""
        _setup_persistence_paths(temp_algopath)
        store = AlgorithmStore()

        store.save_algorithm("algo1", {"text": "t1"})
        store.save_algorithm("algo2", {"text": "t2"})

        algorithms = store.list_algorithms()
        assert "algo1" in algorithms
        assert "algo2" in algorithms

    def test_algorithm_exists(self, temp_algopath):
        """Test checking algorithm existence."""
        _setup_persistence_paths(temp_algopath)
        store = AlgorithmStore()

        assert not store.algorithm_exists("new")
        store.save_algorithm("new", {"text": "x"})
        assert store.algorithm_exists("new")

    def test_delete_algorithm(self, temp_algopath):
        """Test deleting an algorithm."""
        _setup_persistence_paths(temp_algopath)
        store = AlgorithmStore()

        store.save_algorithm("to_delete", {"text": "x"})
        assert store.algorithm_exists("to_delete")
        store.delete_algorithm("to_delete")
        assert not store.algorithm_exists("to_delete")

    def test_save_adds_metadata(self, temp_algopath):
        """Test that save adds timestamps."""
        _setup_persistence_paths(temp_algopath)
        store = AlgorithmStore()

        data = {"text": "test"}
        store.save_algorithm("meta_test", data)

        loaded = store.load_algorithm("meta_test")
        assert "created_at" in loaded
        assert "updated_at" in loaded
        assert "version" in loaded

    def test_load_nonexistent_returns_none(self, temp_algopath):
        """Test loading non-existent algorithm returns None."""
        _setup_persistence_paths(temp_algopath)
        store = AlgorithmStore()

        loaded = store.load_algorithm("does_not_exist")
        assert loaded is None

    def test_delete_nonexistent_returns_false(self, temp_algopath):
        """Test deleting non-existent algorithm returns False."""
        _setup_persistence_paths(temp_algopath)
        store = AlgorithmStore()

        result = store.delete_algorithm("does_not_exist")
        assert result is False


class TestGitManager:
    """Test suite for GitManager."""

    def test_init_repo(self, temp_algopath):
        """Test git repository initialization."""
        algopath = Path(temp_algopath) / ".algomath"
        gm = GitManager(repo_path=algopath)
        gm._ensure_repo()
        assert (algopath / ".git").exists()

    def test_commit_algorithm(self, temp_algopath):
        """Test committing algorithm changes."""
        algopath = Path(temp_algopath) / ".algomath"
        gm = GitManager(repo_path=algopath)
        gm._ensure_repo()

        # Create algorithm directory and file
        algo_dir = algopath / "algorithms" / "test"
        algo_dir.mkdir(parents=True)
        algo_file = algo_dir / "algorithm.json"
        algo_file.write_text(json.dumps({"name": "test"}))

        commit_hash = gm.commit_algorithm("test", "Test commit")
        assert len(commit_hash) == 40

        # Verify commit exists
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=algopath,
            capture_output=True,
            text=True
        )
        assert "Test commit" in result.stdout

    def test_get_version(self, temp_algopath):
        """Test getting version hash."""
        algopath = Path(temp_algopath) / ".algomath"
        gm = GitManager(repo_path=algopath)
        gm._ensure_repo()

        # Create and commit
        algo_dir = algopath / "algorithms" / "test"
        algo_dir.mkdir(parents=True)
        algo_file = algo_dir / "algorithm.json"
        algo_file.write_text(json.dumps({"name": "test"}))

        gm.commit_algorithm("test", "Test commit")

        version = gm.get_version("test")
        assert len(version) == 40  # SHA hash

    def test_get_history(self, temp_algopath):
        """Test getting commit history."""
        algopath = Path(temp_algopath) / ".algomath"
        gm = GitManager(repo_path=algopath)
        gm._ensure_repo()

        # Create and commit multiple times
        algo_dir = algopath / "algorithms" / "test"
        algo_dir.mkdir(parents=True)
        algo_file = algo_dir / "algorithm.json"

        algo_file.write_text(json.dumps({"version": 1}))
        gm.commit_algorithm("test", "First commit")

        algo_file.write_text(json.dumps({"version": 2}))
        gm.commit_algorithm("test", "Second commit")

        history = gm.get_history("test")
        assert len(history) >= 1
        assert any("First commit" in h["message"] for h in history)
        assert any("Second commit" in h["message"] for h in history)

    def test_checkout_version(self, temp_algopath):
        """Test checking out specific version."""
        algopath = Path(temp_algopath) / ".algomath"
        gm = GitManager(repo_path=algopath)
        gm._ensure_repo()

        # Create and commit
        algo_dir = algopath / "algorithms" / "test"
        algo_dir.mkdir(parents=True)
        algo_file = algo_dir / "algorithm.json"
        algo_file.write_text(json.dumps({"version": 1}))

        first_hash = gm.commit_algorithm("test", "First")

        # Modify and commit again
        algo_file.write_text(json.dumps({"version": 2}))
        gm.commit_algorithm("test", "Second")

        # Checkout first version
        result = gm.checkout_version("test", first_hash)
        assert result is True

        # Verify content
        content = json.loads(algo_file.read_text())
        assert content["version"] == 1

    def test_get_version_nonexistent_algorithm(self, temp_algopath):
        """Test getting version of non-existent algorithm."""
        algopath = Path(temp_algopath) / ".algomath"
        gm = GitManager(repo_path=algopath)
        gm._ensure_repo()

        version = gm.get_version("does_not_exist")
        assert version is None

    def test_get_history_nonexistent_algorithm(self, temp_algopath):
        """Test getting history of non-existent algorithm."""
        algopath = Path(temp_algopath) / ".algomath"
        gm = GitManager(repo_path=algopath)
        gm._ensure_repo()

        history = gm.get_history("does_not_exist")
        assert history == []


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_save_and_load_algorithm(self, temp_algopath):
        """Test save_algorithm and load_algorithm functions."""
        _setup_persistence_paths(temp_algopath)
        from algomath.persistence import save_algorithm, load_algorithm

        data = {"text": "test algorithm"}
        commit_hash = save_algorithm("test_func", data)
        assert len(commit_hash) == 40

        loaded = load_algorithm("test_func")
        assert loaded["text"] == "test algorithm"

    def test_list_algorithms_function(self, temp_algopath):
        """Test list_algorithms function."""
        _setup_persistence_paths(temp_algopath)
        from algomath.persistence import save_algorithm, list_algorithms

        save_algorithm("func1", {"text": "t1"})
        save_algorithm("func2", {"text": "t2"})

        algorithms = list_algorithms()
        assert "func1" in algorithms
        assert "func2" in algorithms

    def test_delete_algorithm_function(self, temp_algopath):
        """Test delete_algorithm function."""
        _setup_persistence_paths(temp_algopath)
        from algomath.persistence import save_algorithm, delete_algorithm, algorithm_exists

        save_algorithm("delete_me", {"text": "x"})
        assert algorithm_exists("delete_me")

        delete_algorithm("delete_me")
        assert not algorithm_exists("delete_me")
