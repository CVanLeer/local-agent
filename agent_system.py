#!/usr/bin/env python3
"""Working Agent System using Python API"""

from interpreter import interpreter
import json
from datetime import datetime
from pathlib import Path
import time
from utils.logging import get_logger, AgentLoggerMixin

class LocalAgent(AgentLoggerMixin):
    def __init__(self, model="ollama/qwen2.5-coder:14b-instruct-q4_K_M"):
        """Initialize agent with local model"""
        super().__init__()
        self.model = model
        self.setup_interpreter()
        self.log_info(f"LocalAgent initialized with model: {model}")
        
    def setup_interpreter(self):
        """Configure interpreter for local use"""
        self.log_debug("Setting up interpreter configuration")
        interpreter.llm.model = self.model
        interpreter.local = True
        interpreter.auto_run = True
        interpreter.verbose = False
        interpreter.llm.context_window = 32000
        interpreter.llm.max_tokens = 4096
        interpreter.llm.api_base = "http://localhost:11434/v1"
        self.log_debug("Interpreter configured successfully")
        
    def run(self, prompt):
        """Execute a prompt and return results"""
        start_time = time.time()
        self.log_execution(prompt, "LocalAgent")
        
        try:
            result = interpreter.chat(prompt)
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
            interpreter.reset()  # Clean state for next run
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
