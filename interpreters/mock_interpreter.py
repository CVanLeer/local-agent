"""Mock interpreter for testing"""

import time
import random
from typing import Dict, Any, Optional, List
from .base_interpreter import BaseInterpreter, InterpreterConfig
from utils.logging import get_logger


class MockInterpreter(BaseInterpreter):
    """Mock interpreter for testing without actual execution"""
    
    def __init__(self, config: InterpreterConfig):
        """Initialize mock interpreter"""
        super().__init__(config)
        self.logger = get_logger(self.__class__.__name__)
        self._mock_responses = {
            "default": "Mock execution completed successfully",
            "error": "Mock error occurred",
            "timeout": "Mock timeout occurred"
        }
        self._execution_count = 0
        self._state = {}
        
    def initialize(self) -> None:
        """Initialize mock interpreter"""
        if self._is_initialized:
            return
            
        self._is_initialized = True
        self.logger.info(f"MockInterpreter initialized with model: {self.config.model}")
        
    def chat(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Mock chat execution"""
        if not self._is_initialized:
            self.initialize()
            
        self._execution_count += 1
        
        # Simulate processing time
        time.sleep(random.uniform(0.1, 0.5))
        
        # Simulate different responses based on prompt content
        if "error" in prompt.lower():
            raise RuntimeError(self._mock_responses["error"])
        elif "timeout" in prompt.lower():
            time.sleep(self.config.timeout + 1)
            raise TimeoutError(self._mock_responses["timeout"])
        else:
            response = {
                "response": self._mock_responses["default"],
                "prompt": prompt[:50],
                "context": context,
                "execution_number": self._execution_count,
                "model": self.config.model
            }
            
            self.logger.debug(f"Mock execution #{self._execution_count} completed")
            return response
            
    def reset(self) -> None:
        """Reset mock interpreter state"""
        self._execution_count = 0
        self._state = {}
        self.logger.debug("Mock interpreter reset")
        
    def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Mock code execution"""
        if not self._is_initialized:
            self.initialize()
            
        # Simulate execution
        time.sleep(random.uniform(0.1, 0.3))
        
        if "raise" in code or "error" in code.lower():
            return {
                "success": False,
                "error": "Mock execution error in code",
                "language": language,
                "code": code[:100]
            }
        else:
            return {
                "success": True,
                "output": f"Mock output for {language} code",
                "language": language,
                "code": code[:100],
                "execution_time": random.uniform(0.1, 1.0)
            }
            
    def get_state(self) -> Dict[str, Any]:
        """Get mock interpreter state"""
        return {
            "config": self.config.to_dict(),
            "is_initialized": self._is_initialized,
            "execution_count": self._execution_count,
            "mock_state": self._state,
            "capabilities": self.get_capabilities()
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        """Set mock interpreter state"""
        if "execution_count" in state:
            self._execution_count = state["execution_count"]
        if "mock_state" in state:
            self._state = state["mock_state"]
            
    def validate_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Mock code validation"""
        # Simulate validation
        if "syntax_error" in code.lower():
            return {
                "valid": False,
                "error": "Mock syntax error",
                "line": 1,
                "offset": 10,
                "language": language
            }
        else:
            return {
                "valid": True,
                "language": language
            }
            
    def get_capabilities(self) -> List[str]:
        """Get mock interpreter capabilities"""
        return [
            "mock_chat",
            "mock_execution",
            "testing",
            "simulation",
            "error_injection",
            "timeout_simulation"
        ]
        
    def set_mock_response(self, key: str, response: str) -> None:
        """Set custom mock response for testing"""
        self._mock_responses[key] = response
        
    def get_execution_count(self) -> int:
        """Get number of executions for testing"""
        return self._execution_count