"""OpenInterpreter implementation of BaseInterpreter"""

import time
import ast
from typing import Dict, Any, Optional, List
from .base_interpreter import BaseInterpreter, InterpreterConfig
from utils.logging import get_logger


class OpenInterpreterImpl(BaseInterpreter):
    """Implementation using Open Interpreter"""
    
    def __init__(self, config: InterpreterConfig):
        """Initialize OpenInterpreter implementation"""
        super().__init__(config)
        self.logger = get_logger(self.__class__.__name__)
        self.interpreter = None
        self._execution_history = []
        
    def initialize(self) -> None:
        """Lazy load and configure Open Interpreter"""
        if self._is_initialized:
            return
            
        try:
            # Import only when needed
            import interpreter as oi
            self.interpreter = oi
            
            # Configure based on config
            self.interpreter.llm.model = self.config.model
            self.interpreter.local = (self.config.mode.value == "local")
            self.interpreter.auto_run = self.config.auto_run
            self.interpreter.safe_mode = self.config.safe_mode
            self.interpreter.llm.context_window = self.config.context_window
            self.interpreter.llm.max_tokens = self.config.max_tokens
            self.interpreter.llm.temperature = self.config.temperature
            
            if self.config.api_base:
                self.interpreter.llm.api_base = self.config.api_base
            
            if self.config.api_key:
                self.interpreter.llm.api_key = self.config.api_key
                
            self._is_initialized = True
            self.logger.info(f"OpenInterpreter initialized with model: {self.config.model}")
            
        except ImportError as e:
            self.logger.error("Failed to import interpreter module", exception=e)
            raise RuntimeError("Open Interpreter not installed. Run: pip install open-interpreter")
        except Exception as e:
            self.logger.error("Failed to initialize OpenInterpreter", exception=e)
            raise
            
    def chat(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a chat/code prompt"""
        if not self._is_initialized:
            self.initialize()
            
        start_time = time.time()
        
        # Build prompt with context if provided
        full_prompt = prompt
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            full_prompt = f"Context:\n{context_str}\n\nTask:\n{prompt}"
            
        try:
            self.logger.debug(f"Executing prompt: {prompt[:100]}...")
            result = self.interpreter.chat(full_prompt)
            
            duration = time.time() - start_time
            self._execution_history.append({
                "prompt": prompt,
                "context": context,
                "duration": duration,
                "success": True,
                "timestamp": time.time()
            })
            
            self.logger.info(f"Execution completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self._execution_history.append({
                "prompt": prompt,
                "context": context,
                "duration": duration,
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            })
            
            self.logger.error(f"Execution failed after {duration:.2f}s", exception=e)
            raise
            
    def reset(self) -> None:
        """Reset interpreter state"""
        if self._is_initialized and self.interpreter:
            try:
                self.interpreter.reset()
                self.logger.debug("Interpreter state reset")
            except Exception as e:
                self.logger.warning(f"Failed to reset interpreter: {e}")
                
    def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Execute specific code snippet"""
        if not self._is_initialized:
            self.initialize()
            
        prompt = f"Execute this {language} code:\n```{language}\n{code}\n```"
        
        try:
            result = self.chat(prompt)
            return {
                "success": True,
                "output": result,
                "language": language,
                "code": code
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "language": language,
                "code": code
            }
            
    def get_state(self) -> Dict[str, Any]:
        """Get current interpreter state"""
        return {
            "config": self.config.to_dict(),
            "is_initialized": self._is_initialized,
            "execution_history": self._execution_history[-10:],  # Last 10 executions
            "capabilities": self.get_capabilities()
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        """Restore interpreter state"""
        # For OpenInterpreter, we mainly restore config
        # Actual state restoration would require more complex handling
        if "config" in state:
            # Update config if needed
            pass
            
        if "execution_history" in state:
            self._execution_history = state["execution_history"]
            
    def validate_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Validate code without executing"""
        if language == "python":
            try:
                ast.parse(code)
                return {
                    "valid": True,
                    "language": language
                }
            except SyntaxError as e:
                return {
                    "valid": False,
                    "error": str(e),
                    "line": e.lineno,
                    "offset": e.offset,
                    "language": language
                }
        else:
            # For other languages, we'd need specific validators
            self.logger.warning(f"No validator for language: {language}")
            return {
                "valid": None,
                "message": f"No validator available for {language}",
                "language": language
            }
            
    def get_capabilities(self) -> List[str]:
        """Get list of interpreter capabilities"""
        return [
            "chat",
            "code_execution",
            "multi_language",
            "context_aware",
            "state_management",
            "python_validation",
            "local_models",
            "auto_run"
        ]