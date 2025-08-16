"""Unit tests for LocalAgent class in agent_system.py"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import json
from pathlib import Path

# Import the module to test
from agent_system import LocalAgent


class TestLocalAgent:
    """Test suite for LocalAgent class"""
    
    def test_init_default_model(self):
        """Test LocalAgent initialization with default model"""
        with patch('agent_system.interpreter') as mock_interpreter:
            agent = LocalAgent()
            
            assert agent.model == "ollama/qwen2.5-coder:14b-instruct-q4_K_M"
            assert mock_interpreter.llm.model == agent.model
    
    def test_init_custom_model(self):
        """Test LocalAgent initialization with custom model"""
        custom_model = "ollama/llama2:7b"
        with patch('agent_system.interpreter') as mock_interpreter:
            agent = LocalAgent(model=custom_model)
            
            assert agent.model == custom_model
            assert mock_interpreter.llm.model == custom_model
    
    def test_setup_interpreter_configuration(self):
        """Test that interpreter is configured correctly"""
        with patch('agent_system.interpreter') as mock_interpreter:
            agent = LocalAgent()
            
            # Verify all interpreter settings
            assert mock_interpreter.llm.model == agent.model
            assert mock_interpreter.local == True
            assert mock_interpreter.auto_run == True
            assert mock_interpreter.verbose == False
            assert mock_interpreter.llm.context_window == 32000
            assert mock_interpreter.llm.max_tokens == 4096
            assert mock_interpreter.llm.api_base == "http://localhost:11434/v1"
    
    @patch('agent_system.interpreter')
    def test_run_successful_execution(self, mock_interpreter):
        """Test successful prompt execution"""
        # Setup mock response
        mock_response = [{"content": "Task completed successfully"}]
        mock_interpreter.chat.return_value = mock_response
        
        agent = LocalAgent()
        prompt = "Test prompt"
        
        result = agent.run(prompt)
        
        # Verify the result structure
        assert result["success"] == True
        assert result["output"] == mock_response
        assert "timestamp" in result
        
        # Verify interpreter was called correctly
        mock_interpreter.chat.assert_called_once_with(prompt)
        mock_interpreter.reset.assert_called_once()
    
    @patch('agent_system.interpreter')
    def test_run_handles_exception(self, mock_interpreter):
        """Test exception handling during execution"""
        # Setup mock to raise exception
        error_message = "Connection failed"
        mock_interpreter.chat.side_effect = Exception(error_message)
        
        agent = LocalAgent()
        prompt = "Test prompt"
        
        result = agent.run(prompt)
        
        # Verify error handling
        assert result["success"] == False
        assert result["error"] == error_message
        assert "timestamp" in result
        
        # Verify reset was still called
        mock_interpreter.reset.assert_called_once()
    
    @patch('agent_system.interpreter')
    def test_run_always_resets_interpreter(self, mock_interpreter):
        """Test that interpreter.reset() is always called, even on error"""
        # Test with success
        mock_interpreter.chat.return_value = [{"content": "Success"}]
        agent = LocalAgent()
        agent.run("test")
        assert mock_interpreter.reset.call_count == 1
        
        # Test with failure
        mock_interpreter.chat.side_effect = Exception("Error")
        agent.run("test")
        assert mock_interpreter.reset.call_count == 2
    
    @patch('agent_system.interpreter')
    def test_run_timestamp_format(self, mock_interpreter):
        """Test that timestamp is in correct ISO format"""
        mock_interpreter.chat.return_value = [{"content": "Success"}]
        
        agent = LocalAgent()
        result = agent.run("test")
        
        # Verify timestamp can be parsed as ISO format
        timestamp = result["timestamp"]
        parsed_time = datetime.fromisoformat(timestamp)
        assert isinstance(parsed_time, datetime)
    
    @patch('agent_system.interpreter')
    def test_run_truncates_long_prompt_in_output(self, mock_interpreter, capsys):
        """Test that long prompts are truncated in console output"""
        mock_interpreter.chat.return_value = [{"content": "Success"}]
        
        agent = LocalAgent()
        long_prompt = "x" * 150  # Create a prompt longer than 100 chars
        
        agent.run(long_prompt)
        
        captured = capsys.readouterr()
        assert "🤖 Executing: " in captured.out
        assert "x" * 100 in captured.out  # First 100 chars should be shown
        assert "..." in captured.out  # Ellipsis should be added
    
    @patch('agent_system.interpreter')
    def test_multiple_runs_maintain_clean_state(self, mock_interpreter):
        """Test that multiple runs don't interfere with each other"""
        mock_interpreter.chat.return_value = [{"content": "Success"}]
        
        agent = LocalAgent()
        
        # Run multiple times
        result1 = agent.run("prompt1")
        result2 = agent.run("prompt2")
        result3 = agent.run("prompt3")
        
        # Each run should reset the interpreter
        assert mock_interpreter.reset.call_count == 3
        
        # Each result should be independent
        assert result1["success"] == True
        assert result2["success"] == True
        assert result3["success"] == True
    
    @patch('agent_system.interpreter')
    def test_run_with_empty_prompt(self, mock_interpreter):
        """Test behavior with empty prompt"""
        mock_interpreter.chat.return_value = []
        
        agent = LocalAgent()
        result = agent.run("")
        
        # Should still execute and return valid structure
        assert "success" in result
        assert "timestamp" in result
        mock_interpreter.chat.assert_called_once_with("")
    
    @patch('agent_system.interpreter')
    def test_run_with_none_response(self, mock_interpreter):
        """Test handling of None response from interpreter"""
        mock_interpreter.chat.return_value = None
        
        agent = LocalAgent()
        result = agent.run("test")
        
        assert result["success"] == True
        assert result["output"] is None
        assert "timestamp" in result


class TestLocalAgentIntegration:
    """Integration tests for LocalAgent (requires mock Ollama)"""
    
    @pytest.mark.skip(reason="Requires Ollama server running")
    def test_real_calculation(self):
        """Integration test with real interpreter (skip in CI)"""
        agent = LocalAgent()
        result = agent.run("Calculate 2 + 2")
        
        assert result["success"] == True
        assert result["output"] is not None
    
    @patch('agent_system.interpreter')
    def test_concurrent_agents(self, mock_interpreter):
        """Test multiple LocalAgent instances don't interfere"""
        mock_interpreter.chat.return_value = [{"content": "Success"}]
        
        agent1 = LocalAgent("model1")
        agent2 = LocalAgent("model2")
        
        # Each agent should have its own model
        assert agent1.model == "model1"
        assert agent2.model == "model2"
        
        # Running agents shouldn't interfere
        result1 = agent1.run("test1")
        result2 = agent2.run("test2")
        
        assert result1["success"] == True
        assert result2["success"] == True