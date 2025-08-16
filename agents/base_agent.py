"""Base Agent class hierarchy for local-agent system"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid
from datetime import datetime

from utils.logging import AgentLoggerMixin
from interpreters import BaseInterpreter
from config import get_config


class AgentRole(Enum):
    """Predefined agent roles"""
    CODER = "coder"
    REVIEWER = "reviewer"
    TESTER = "tester"
    ARCHITECT = "architect"
    DEBUGGER = "debugger"
    DOCUMENTER = "documenter"
    ANALYST = "analyst"
    GENERAL = "general"


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    BUSY = "busy"
    FAILED = "failed"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


@dataclass
class AgentMetadata:
    """Metadata for agent instances"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    role: AgentRole = AgentRole.GENERAL
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value,
            "created_at": self.created_at.isoformat(),
            "version": self.version,
            "tags": self.tags
        }


@dataclass
class AgentCapabilities:
    """Defines what an agent can do"""
    can_execute_code: bool = True
    can_access_files: bool = True
    can_make_network_calls: bool = False
    can_spawn_agents: bool = False
    can_modify_system: bool = False
    max_execution_time: int = 300
    allowed_languages: List[str] = field(default_factory=lambda: ["python"])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert capabilities to dictionary"""
        return {
            "can_execute_code": self.can_execute_code,
            "can_access_files": self.can_access_files,
            "can_make_network_calls": self.can_make_network_calls,
            "can_spawn_agents": self.can_spawn_agents,
            "can_modify_system": self.can_modify_system,
            "max_execution_time": self.max_execution_time,
            "allowed_languages": self.allowed_languages
        }


class BaseAgent(ABC, AgentLoggerMixin):
    """Abstract base class for all agents"""
    
    def __init__(
        self,
        interpreter: BaseInterpreter,
        metadata: Optional[AgentMetadata] = None,
        capabilities: Optional[AgentCapabilities] = None
    ):
        """
        Initialize base agent
        
        Args:
            interpreter: Interpreter implementation
            metadata: Agent metadata
            capabilities: Agent capabilities
        """
        super().__init__()
        self.interpreter = interpreter
        self.metadata = metadata or AgentMetadata()
        self.capabilities = capabilities or AgentCapabilities()
        self.status = AgentStatus.IDLE
        self.execution_history: List[Dict[str, Any]] = []
        self.config = get_config()
        
        # Callbacks
        self._on_start_callbacks: List[Callable] = []
        self._on_complete_callbacks: List[Callable] = []
        self._on_error_callbacks: List[Callable] = []
        
        self.log_info(f"Initialized {self.__class__.__name__} with role: {self.metadata.role.value}")
        
    @abstractmethod
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a task
        
        Args:
            task: Task description or prompt
            context: Optional execution context
            
        Returns:
            Execution result dictionary
        """
        pass
    
    @abstractmethod
    def validate_task(self, task: str) -> bool:
        """
        Validate if agent can handle the task
        
        Args:
            task: Task to validate
            
        Returns:
            True if task is valid
        """
        pass
    
    def pre_execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Hook called before execution"""
        self.status = AgentStatus.BUSY
        self.log_debug(f"Pre-execution: {task[:100]}...")
        
        # Run callbacks
        for callback in self._on_start_callbacks:
            try:
                callback(self, task, context)
            except Exception as e:
                self.log_warning(f"Callback error: {e}")
                
    def post_execute(self, result: Dict[str, Any]) -> None:
        """Hook called after execution"""
        self.status = AgentStatus.IDLE
        self.log_debug("Post-execution completed")
        
        # Run callbacks
        for callback in self._on_complete_callbacks:
            try:
                callback(self, result)
            except Exception as e:
                self.log_warning(f"Callback error: {e}")
                
    def handle_error(self, error: Exception, task: str) -> Dict[str, Any]:
        """
        Handle execution errors
        
        Args:
            error: Exception that occurred
            task: Task that failed
            
        Returns:
            Error result dictionary
        """
        self.status = AgentStatus.FAILED
        self.log_error(f"Task failed: {task[:100]}...", exception=error)
        
        result = {
            "success": False,
            "error": str(error),
            "error_type": type(error).__name__,
            "task": task,
            "agent_id": self.metadata.id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Run error callbacks
        for callback in self._on_error_callbacks:
            try:
                callback(self, error, task)
            except Exception as e:
                self.log_warning(f"Error callback failed: {e}")
                
        return result
    
    def add_callback(self, event: str, callback: Callable) -> None:
        """
        Add event callback
        
        Args:
            event: Event type (start, complete, error)
            callback: Callback function
        """
        if event == "start":
            self._on_start_callbacks.append(callback)
        elif event == "complete":
            self._on_complete_callbacks.append(callback)
        elif event == "error":
            self._on_error_callbacks.append(callback)
        else:
            raise ValueError(f"Unknown event type: {event}")
            
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information"""
        return {
            "id": self.metadata.id,
            "name": self.metadata.name,
            "role": self.metadata.role.value,
            "status": self.status.value,
            "capabilities": self.capabilities.to_dict(),
            "execution_count": len(self.execution_history),
            "last_execution": self.execution_history[-1] if self.execution_history else None
        }
        
    def reset(self) -> None:
        """Reset agent state"""
        self.status = AgentStatus.IDLE
        self.interpreter.reset()
        self.log_debug("Agent state reset")
        
    def suspend(self) -> None:
        """Suspend agent operations"""
        self.status = AgentStatus.SUSPENDED
        self.log_info("Agent suspended")
        
    def resume(self) -> None:
        """Resume agent operations"""
        if self.status == AgentStatus.SUSPENDED:
            self.status = AgentStatus.IDLE
            self.log_info("Agent resumed")
            
    def terminate(self) -> None:
        """Terminate agent"""
        self.status = AgentStatus.TERMINATED
        self.reset()
        self.log_info("Agent terminated")
        

class SimpleAgent(BaseAgent):
    """Simple implementation of BaseAgent"""
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a simple task"""
        if not self.validate_task(task):
            return self.handle_error(ValueError("Invalid task"), task)
            
        self.pre_execute(task, context)
        start_time = time.time()
        
        try:
            # Execute via interpreter
            result = self.interpreter.chat(task, context)
            duration = time.time() - start_time
            
            execution_result = {
                "success": True,
                "output": result,
                "task": task,
                "context": context,
                "agent_id": self.metadata.id,
                "agent_role": self.metadata.role.value,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            
            self.execution_history.append(execution_result)
            self.post_execute(execution_result)
            
            return execution_result
            
        except Exception as e:
            return self.handle_error(e, task)
            
    def validate_task(self, task: str) -> bool:
        """Validate task is not empty"""
        return bool(task and task.strip())


class SpecializedAgent(BaseAgent):
    """Base class for specialized agents with custom prompts"""
    
    def __init__(
        self,
        interpreter: BaseInterpreter,
        system_prompt: str,
        metadata: Optional[AgentMetadata] = None,
        capabilities: Optional[AgentCapabilities] = None
    ):
        """Initialize specialized agent with system prompt"""
        super().__init__(interpreter, metadata, capabilities)
        self.system_prompt = system_prompt
        
    def build_prompt(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Build full prompt with system prompt and context
        
        Args:
            task: User task
            context: Optional context
            
        Returns:
            Complete prompt
        """
        prompt_parts = [self.system_prompt]
        
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            prompt_parts.append(f"Context:\n{context_str}")
            
        prompt_parts.append(f"Task:\n{task}")
        
        return "\n\n".join(prompt_parts)
        
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute with specialized prompt"""
        if not self.validate_task(task):
            return self.handle_error(ValueError("Invalid task"), task)
            
        self.pre_execute(task, context)
        start_time = time.time()
        
        try:
            # Build full prompt
            full_prompt = self.build_prompt(task, context)
            
            # Execute via interpreter
            result = self.interpreter.chat(full_prompt)
            duration = time.time() - start_time
            
            execution_result = {
                "success": True,
                "output": result,
                "task": task,
                "context": context,
                "agent_id": self.metadata.id,
                "agent_role": self.metadata.role.value,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            
            self.execution_history.append(execution_result)
            self.post_execute(execution_result)
            
            return execution_result
            
        except Exception as e:
            return self.handle_error(e, task)
            
    def validate_task(self, task: str) -> bool:
        """Validate task is appropriate for this agent"""
        # Can be overridden by subclasses for specific validation
        return bool(task and task.strip())