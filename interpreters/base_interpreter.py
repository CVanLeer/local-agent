"""Base interpreter interface for code execution"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class InterpreterMode(Enum):
    """Execution modes for interpreters"""
    LOCAL = "local"
    REMOTE = "remote"
    SANDBOX = "sandbox"


@dataclass
class InterpreterConfig:
    """Configuration for interpreter instances"""
    model: str
    mode: InterpreterMode = InterpreterMode.LOCAL
    context_window: int = 32000
    max_tokens: int = 4096
    temperature: float = 0.7
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    auto_run: bool = True
    safe_mode: bool = True
    timeout: int = 300  # 5 minutes default
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "model": self.model,
            "mode": self.mode.value,
            "context_window": self.context_window,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "api_base": self.api_base,
            "api_key": self.api_key,
            "auto_run": self.auto_run,
            "safe_mode": self.safe_mode,
            "timeout": self.timeout
        }


class BaseInterpreter(ABC):
    """Abstract base class for code interpreters"""
    
    def __init__(self, config: InterpreterConfig):
        """
        Initialize interpreter with configuration
        
        Args:
            config: Interpreter configuration object
        """
        self.config = config
        self._is_initialized = False
        
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the interpreter (lazy loading)"""
        pass
    
    @abstractmethod
    def chat(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a chat/code prompt
        
        Args:
            prompt: The prompt to execute
            context: Optional context dictionary
            
        Returns:
            Execution result
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset interpreter state"""
        pass
    
    @abstractmethod
    def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Execute specific code snippet
        
        Args:
            code: Code to execute
            language: Programming language
            
        Returns:
            Execution result with output and errors
        """
        pass
    
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Get current interpreter state"""
        pass
    
    @abstractmethod
    def set_state(self, state: Dict[str, Any]) -> None:
        """Restore interpreter state"""
        pass
    
    @abstractmethod
    def validate_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Validate code without executing
        
        Args:
            code: Code to validate
            language: Programming language
            
        Returns:
            Validation result with any syntax errors
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Get list of interpreter capabilities"""
        pass
    
    def __enter__(self):
        """Context manager entry"""
        if not self._is_initialized:
            self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.reset()
        return False