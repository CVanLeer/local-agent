"""Unit tests for MultiAgentSystem class in multi_agent.py"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import json
import time
from typing import Dict, List

# Import the module to test
from multi_agent import MultiAgentSystem


class TestMultiAgentSystem:
    """Test suite for MultiAgentSystem class"""
    
    def test_init(self):
        """Test MultiAgentSystem initialization"""
        system = MultiAgentSystem()
        
        assert system.model == "ollama/qwen2.5-coder:14b-instruct-q4_K_M"
        assert system.agents == {}
        assert system.results == []
    
    def test_create_agent(self):
        """Test agent creation"""
        system = MultiAgentSystem()
        
        # Create an agent
        system.create_agent("test_agent", "test role")
        
        assert "test_agent" in system.agents
        assert system.agents["test_agent"]["role"] == "test role"
        assert "created" in system.agents["test_agent"]
        assert isinstance(system.agents["test_agent"]["created"], float)
    
    def test_create_multiple_agents(self):
        """Test creating multiple agents"""
        system = MultiAgentSystem()
        
        system.create_agent("agent1", "role1")
        system.create_agent("agent2", "role2")
        system.create_agent("agent3", "role3")
        
        assert len(system.agents) == 3
        assert all(name in system.agents for name in ["agent1", "agent2", "agent3"])
    
    def test_create_agent_overwrites_existing(self):
        """Test that creating an agent with same name overwrites the old one"""
        system = MultiAgentSystem()
        
        system.create_agent("agent", "old_role")
        old_created = system.agents["agent"]["created"]
        
        time.sleep(0.01)  # Ensure different timestamp
        system.create_agent("agent", "new_role")
        
        assert system.agents["agent"]["role"] == "new_role"
        assert system.agents["agent"]["created"] > old_created
    
    @patch('multi_agent.interpreter')
    def test_run_agent_successful(self, mock_interpreter):
        """Test successful agent execution"""
        mock_interpreter.chat.return_value = [{"content": "Task completed"}]
        
        system = MultiAgentSystem()
        system.create_agent("test_agent", "test role")
        
        result = system.run_agent("test_agent", "test task", {"key": "value"})
        
        assert result["success"] == True
        assert result["agent"] == "test_agent"
        assert result["task"] == "test task"
        assert result["output"] == [{"content": "Task completed"}]
        assert "timestamp" in result
        
        # Verify interpreter was configured
        assert mock_interpreter.llm.model == system.model
        assert mock_interpreter.local == True
        assert mock_interpreter.auto_run == True
        assert mock_interpreter.verbose == False
        
        # Verify reset was called
        mock_interpreter.reset.assert_called_once()
    
    @patch('multi_agent.interpreter')
    def test_run_agent_with_error(self, mock_interpreter):
        """Test agent execution with error"""
        mock_interpreter.chat.side_effect = Exception("Test error")
        
        system = MultiAgentSystem()
        system.create_agent("test_agent", "test role")
        
        result = system.run_agent("test_agent", "test task")
        
        assert result["success"] == False
        assert result["error"] == "Test error"
        assert result["agent"] == "test_agent"
        assert result["task"] == "test task"
        
        # Verify reset was still called
        mock_interpreter.reset.assert_called_once()
    
    @patch('multi_agent.interpreter')
    def test_run_agent_creates_if_not_exists(self, mock_interpreter):
        """Test that run_agent creates agent if it doesn't exist"""
        mock_interpreter.chat.return_value = [{"content": "Done"}]
        
        system = MultiAgentSystem()
        
        # Run agent without creating it first
        result = system.run_agent("new_agent", "task")
        
        # Agent should be created with default role
        assert "new_agent" in system.agents
        assert system.agents["new_agent"]["role"] == "general assistant"
    
    @patch('multi_agent.interpreter')
    def test_run_agent_with_context(self, mock_interpreter):
        """Test agent execution with context"""
        mock_interpreter.chat.return_value = [{"content": "Done"}]
        
        system = MultiAgentSystem()
        context = {"previous": "data", "config": {"key": "value"}}
        
        result = system.run_agent("agent", "task", context)
        
        # Verify context was included in prompt
        call_args = mock_interpreter.chat.call_args[0][0]
        assert "Context: " in call_args
        assert json.dumps(context) in call_args
    
    @patch('multi_agent.interpreter')
    def test_run_agent_prompt_construction(self, mock_interpreter):
        """Test that agent prompt is constructed correctly"""
        mock_interpreter.chat.return_value = [{"content": "Done"}]
        
        system = MultiAgentSystem()
        system.create_agent("analyzer", "code analyzer")
        
        system.run_agent("analyzer", "analyze this code", {"file": "test.py"})
        
        prompt = mock_interpreter.chat.call_args[0][0]
        
        assert "You are a code analyzer" in prompt
        assert "Task: analyze this code" in prompt
        assert '"file": "test.py"' in prompt
    
    @patch('multi_agent.interpreter')
    def test_run_pipeline_basic(self, mock_interpreter):
        """Test basic pipeline execution"""
        mock_interpreter.chat.return_value = [{"content": "Step completed"}]
        
        system = MultiAgentSystem()
        
        pipeline = [
            {"agent": "agent1", "task": "task1"},
            {"agent": "agent2", "task": "task2"},
        ]
        
        results = system.run_pipeline(pipeline)
        
        assert len(results) == 2
        assert all(r["success"] for r in results)
        assert results[0]["agent"] == "agent1"
        assert results[1]["agent"] == "agent2"
        
        # Verify interpreter was reset after each task
        assert mock_interpreter.reset.call_count == 2
    
    @patch('multi_agent.interpreter')
    def test_run_pipeline_with_roles(self, mock_interpreter):
        """Test pipeline with agent roles"""
        mock_interpreter.chat.return_value = [{"content": "Done"}]
        
        system = MultiAgentSystem()
        
        pipeline = [
            {"agent": "analyzer", "role": "code analyzer", "task": "analyze"},
            {"agent": "fixer", "role": "bug fixer", "task": "fix bugs"},
        ]
        
        system.run_pipeline(pipeline)
        
        assert system.agents["analyzer"]["role"] == "code analyzer"
        assert system.agents["fixer"]["role"] == "bug fixer"
    
    @patch('multi_agent.interpreter')
    def test_run_pipeline_with_use_previous(self, mock_interpreter):
        """Test pipeline with use_previous flag"""
        # First call returns result, second uses it
        mock_interpreter.chat.side_effect = [
            [{"content": "First result"}],
            [{"content": "Second result"}]
        ]
        
        system = MultiAgentSystem()
        
        pipeline = [
            {"agent": "first", "task": "generate data"},
            {"agent": "second", "task": "process data", "use_previous": True},
        ]
        
        results = system.run_pipeline(pipeline)
        
        # Check second call included previous result in context
        second_call_prompt = mock_interpreter.chat.call_args_list[1][0][0]
        assert "previous_result" in second_call_prompt
        assert "First result" in second_call_prompt
    
    @patch('multi_agent.interpreter')
    def test_run_pipeline_with_existing_context(self, mock_interpreter):
        """Test pipeline preserves existing context when adding previous results"""
        mock_interpreter.chat.side_effect = [
            [{"content": "First"}],
            [{"content": "Second"}]
        ]
        
        system = MultiAgentSystem()
        
        pipeline = [
            {"agent": "first", "task": "task1"},
            {
                "agent": "second", 
                "task": "task2", 
                "context": {"existing": "data"},
                "use_previous": True
            },
        ]
        
        system.run_pipeline(pipeline)
        
        # Verify both existing and previous context are included
        second_prompt = mock_interpreter.chat.call_args_list[1][0][0]
        assert '"existing": "data"' in second_prompt
        assert "previous_result" in second_prompt
    
    @patch('multi_agent.interpreter')
    def test_run_pipeline_continue_on_error_true(self, mock_interpreter):
        """Test pipeline continues when continue_on_error is True"""
        mock_interpreter.chat.side_effect = [
            [{"content": "Success"}],
            Exception("Error in middle"),
            [{"content": "Success after error"}]
        ]
        
        system = MultiAgentSystem()
        
        pipeline = [
            {"agent": "first", "task": "task1"},
            {"agent": "second", "task": "task2", "continue_on_error": True},
            {"agent": "third", "task": "task3"},
        ]
        
        results = system.run_pipeline(pipeline)
        
        assert len(results) == 3
        assert results[0]["success"] == True
        assert results[1]["success"] == False
        assert results[2]["success"] == True
    
    @patch('multi_agent.interpreter')
    def test_run_pipeline_continue_on_error_false(self, mock_interpreter):
        """Test pipeline stops when continue_on_error is False"""
        mock_interpreter.chat.side_effect = [
            [{"content": "Success"}],
            Exception("Error - should stop"),
            [{"content": "Should not reach"}]
        ]
        
        system = MultiAgentSystem()
        
        pipeline = [
            {"agent": "first", "task": "task1"},
            {"agent": "second", "task": "task2", "continue_on_error": False},
            {"agent": "third", "task": "task3"},
        ]
        
        results = system.run_pipeline(pipeline)
        
        # Pipeline should stop after error
        assert len(results) == 2
        assert results[0]["success"] == True
        assert results[1]["success"] == False
    
    @patch('multi_agent.interpreter')
    def test_run_pipeline_empty(self, mock_interpreter):
        """Test running empty pipeline"""
        system = MultiAgentSystem()
        results = system.run_pipeline([])
        
        assert results == []
        mock_interpreter.chat.assert_not_called()
    
    @patch('multi_agent.interpreter')
    @patch('builtins.print')
    def test_run_pipeline_output(self, mock_print, mock_interpreter):
        """Test pipeline progress output"""
        mock_interpreter.chat.return_value = [{"content": "Done"}]
        
        system = MultiAgentSystem()
        pipeline = [
            {"agent": "test", "task": "task"}
        ]
        
        system.run_pipeline(pipeline)
        
        # Verify progress output
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Step 1/1" in str(call) for call in print_calls)
        assert any("🤖 test: Starting task" in str(call) for call in print_calls)
    
    def test_results_persistence(self):
        """Test that results are accumulated across multiple operations"""
        with patch('multi_agent.interpreter') as mock_interpreter:
            mock_interpreter.chat.return_value = [{"content": "Done"}]
            
            system = MultiAgentSystem()
            
            # Run multiple agents
            system.run_agent("agent1", "task1")
            system.run_agent("agent2", "task2")
            
            # Run a pipeline
            pipeline = [{"agent": "agent3", "task": "task3"}]
            system.run_pipeline(pipeline)
            
            # All results should be stored
            assert len(system.results) == 3
            assert [r["agent"] for r in system.results] == ["agent1", "agent2", "agent3"]


class TestMultiAgentSystemIntegration:
    """Integration tests for MultiAgentSystem"""
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires Ollama server")
    def test_real_pipeline_execution(self):
        """Integration test with real interpreter"""
        system = MultiAgentSystem()
        
        pipeline = [
            {
                "agent": "calculator",
                "role": "math calculator",
                "task": "Calculate 10 + 20"
            }
        ]
        
        results = system.run_pipeline(pipeline)
        assert len(results) == 1
        assert results[0]["success"] == True