#!/usr/bin/env python3
"""Working Agent System using Python API"""

import json
from datetime import datetime
from pathlib import Path
import time
from typing import Optional, Dict, Any

from utils.logging import get_logger, AgentLoggerMixin
from interpreters import BaseInterpreter, OpenInterpreterImpl, MockInterpreter
from interpreters.base_interpreter import InterpreterConfig, InterpreterMode

class LocalAgent(AgentLoggerMixin):
    def __init__(self, 
                 model="ollama/qwen2.5-coder:14b-instruct-q4_K_M",
                 interpreter_impl: Optional[BaseInterpreter] = None,
                 test_mode: bool = False):
        """Initialize agent with local model
        
        Args:
            model: Model to use for inference
            interpreter_impl: Optional interpreter implementation
            test_mode: Use mock interpreter for testing
        """
        super().__init__()
        self.model = model
        
        # Setup interpreter based on mode
        if interpreter_impl:
            self.interpreter = interpreter_impl
        elif test_mode:
            config = InterpreterConfig(
                model=model,
                mode=InterpreterMode.LOCAL
            )
            self.interpreter = MockInterpreter(config)
        else:
            config = InterpreterConfig(
                model=model,
                mode=InterpreterMode.LOCAL,
                api_base="http://localhost:11434/v1"
            )
            self.interpreter = OpenInterpreterImpl(config)
        
        self.interpreter.initialize()
        self.log_info(f"LocalAgent initialized with model: {model}")
        
    def run(self, prompt: str, context: Optional[Dict[str, Any]] = None):
        """Execute a prompt and return results
        
        Args:
            prompt: The prompt to execute
            context: Optional context for execution
        """
        start_time = time.time()
        self.log_execution(prompt, "LocalAgent")
        
        try:
            result = self.interpreter.chat(prompt, context)
            duration = time.time() - start_time
            
            self.log_result(True, duration)
            self.log_debug(f"Output length: {len(str(result))} chars")
            
            return {
                "success": True,
                "output": result,
                "timestamp": datetime.now().isoformat(),
                "duration": duration
            }
        except Exception as e:
            duration = time.time() - start_time
            self.log_error(f"Execution failed after {duration:.2f}s", exception=e)
            
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "duration": duration
            }
        finally:
            self.interpreter.reset()  # Clean state for next run
            self.log_debug("Interpreter state reset")

# Test it
if __name__ == "__main__":
    from utils.logging import setup_logging
    
    # Setup logging for testing
    setup_logging(log_level="DEBUG", log_dir=Path("logs"))
    
    agent = LocalAgent()
    
    # Test 1: Simple calculation
    result = agent.run("Calculate 10 factorial and show the result")
    print(f"Result: {json.dumps(result, indent=2)}")
    
    # Test 2: Code generation
    result = agent.run("Write a Python function to check if a number is prime and save it to prime_checker.py")
    print(f"Result: {json.dumps(result, indent=2)}")
