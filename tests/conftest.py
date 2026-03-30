"""
Pytest configuration and fixtures for AlgoMath tests.

This module provides shared fixtures for testing the AlgoMath framework,
enabling isolated test environments with temporary storage.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_algopath():
    """Create temporary .algomath/ directory for tests."""
    temp_dir = tempfile.mkdtemp()
    algopath = Path(temp_dir) / ".algomath"
    algopath.mkdir(parents=True, exist_ok=True)
    yield temp_dir  # Return the temp_dir, not the .algomath subdir
    shutil.rmtree(temp_dir)


@pytest.fixture
def context_manager(temp_algopath):
    """Provide ContextManager with temp storage."""
    from algomath.context import ContextManager
    from algomath.persistence import ALGOMATH_DIR, ALGORITHMS_DIR
    from algomath.state import ALGOMATH_DIR as STATE_ALGOMATH_DIR, SESSION_FILE

    # Patch base paths before creating manager
    import algomath.persistence as persist_module
    import algomath.state as state_module

    algopath = Path(temp_algopath) / ".algomath"
    persist_module.ALGOMATH_DIR = algopath
    persist_module.ALGORITHMS_DIR = algopath / "algorithms"
    state_module.ALGOMATH_DIR = algopath
    state_module.SESSION_FILE = algopath / "session.json"

    cm = ContextManager()
    return cm


@pytest.fixture
def algorithm_store(temp_algopath):
    """Provide AlgorithmStore with temp storage."""
    from algomath.persistence import AlgorithmStore
    import algomath.persistence as persist_module

    algopath = Path(temp_algopath) / ".algomath"
    persist_module.ALGOMATH_DIR = algopath
    persist_module.ALGORITHMS_DIR = algopath / "algorithms"

    store = AlgorithmStore()
    return store


@pytest.fixture
def git_manager(temp_algopath):
    """Provide GitManager with temp storage."""
    from algomath.persistence import GitManager
    gm = GitManager(repo_path=Path(temp_algopath) / ".algomath")
    return gm
