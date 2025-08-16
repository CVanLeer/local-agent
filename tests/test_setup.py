"""Basic test to verify test infrastructure is working"""

import pytest
import sys
from pathlib import Path


def test_python_version():
    """Verify Python version is 3.8 or higher"""
    assert sys.version_info >= (3, 8), "Python 3.8+ required"


def test_project_structure():
    """Verify project structure is correct"""
    project_root = Path(__file__).parent.parent
    
    # Check key files exist
    assert (project_root / "agent_system.py").exists()
    assert (project_root / "multi_agent.py").exists()
    assert (project_root / "requirements.txt").exists()
    
    # Check directories exist
    assert (project_root / "agents").is_dir()
    assert (project_root / "tests").is_dir()


def test_imports():
    """Verify main modules can be imported"""
    try:
        import agent_system
        import multi_agent
    except ImportError as e:
        pytest.fail(f"Failed to import module: {e}")


@pytest.mark.unit
def test_marker_works():
    """Test that pytest markers are working"""
    assert True, "Unit test marker is functional"