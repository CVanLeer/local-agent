"""Pytest configuration and shared fixtures"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_interpreter():
    """Mock interpreter object for testing"""
    mock = MagicMock()
    mock.llm = MagicMock()
    mock.chat = MagicMock()
    mock.reset = MagicMock()
    return mock


@pytest.fixture
def sample_prompt():
    """Sample prompt for testing"""
    return "Calculate 10 factorial and show the result"


@pytest.fixture
def sample_code_prompt():
    """Sample code generation prompt"""
    return "Write a Python function to check if a number is prime"


@pytest.fixture
def mock_successful_response():
    """Mock successful interpreter response"""
    return [
        {
            "role": "assistant",
            "type": "message",
            "content": "The factorial of 10 is 3628800"
        }
    ]


@pytest.fixture
def mock_error_response():
    """Mock error response"""
    return Exception("Connection timeout to Ollama server")