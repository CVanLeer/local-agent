"""Logging configuration for local-agent system"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from loguru import logger
import json


class InterceptHandler(logging.Handler):
    """Handler to intercept standard logging and route to loguru"""
    
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    json_logs: bool = False,
    console: bool = True
):
    """
    Setup comprehensive logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to save log files (creates if not exists)
        json_logs: Whether to output logs in JSON format
        console: Whether to output logs to console
    """
    
    # Remove default logger
    logger.remove()
    
    # Create log directory if specified
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Console logging
    if console:
        if json_logs:
            logger.add(
                sys.stdout,
                format="{message}",
                level=log_level,
                serialize=True
            )
        else:
            logger.add(
                sys.stdout,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                       "<level>{level: <8}</level> | "
                       "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                       "<level>{message}</level>",
                level=log_level,
                colorize=True
            )
    
    # File logging
    if log_dir:
        # General log file
        logger.add(
            log_dir / "local_agent_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=log_level,
            rotation="1 day",
            retention="30 days",
            compression="zip"
        )
        
        # Error log file
        logger.add(
            log_dir / "errors_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="ERROR",
            rotation="1 week",
            retention="3 months",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # JSON log file for structured logging
        if json_logs:
            logger.add(
                log_dir / "local_agent_{time:YYYY-MM-DD}.json",
                format="{message}",
                level=log_level,
                rotation="1 day",
                retention="7 days",
                serialize=True
            )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    
    # Intercept specific libraries
    for name in ["interpreter", "urllib3", "httpx"]:
        logging.getLogger(name).handlers = [InterceptHandler()]
    
    logger.info(f"Logging initialized | Level: {log_level} | JSON: {json_logs}")
    if log_dir:
        logger.info(f"Log files will be saved to: {log_dir.absolute()}")
    
    return logger


def get_logger(name: str = None):
    """
    Get a configured logger instance
    
    Args:
        name: Logger name (typically __name__ from the calling module)
    
    Returns:
        Configured loguru logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger


class AgentLoggerMixin:
    """Mixin class to add logging capabilities to agents"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = get_logger(self.__class__.__name__)
    
    def log_debug(self, message: str, **kwargs):
        """Log debug message with context"""
        self._logger.debug(message, **kwargs)
    
    def log_info(self, message: str, **kwargs):
        """Log info message with context"""
        self._logger.info(message, **kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log warning message with context"""
        self._logger.warning(message, **kwargs)
    
    def log_error(self, message: str, exception: Exception = None, **kwargs):
        """Log error message with exception details"""
        if exception:
            self._logger.error(f"{message} | Error: {str(exception)}", **kwargs)
            self._logger.exception(exception)
        else:
            self._logger.error(message, **kwargs)
    
    def log_success(self, message: str, **kwargs):
        """Log success message"""
        self._logger.success(message, **kwargs)
    
    def log_execution(self, task: str, agent_name: str = None):
        """Log agent execution start"""
        agent = agent_name or getattr(self, 'agent_type', 'Unknown')
        self._logger.info(f"🤖 {agent} | Starting: {task[:100]}...")
    
    def log_result(self, success: bool, duration: float = None):
        """Log execution result"""
        if success:
            msg = "✅ Task completed successfully"
            if duration:
                msg += f" | Duration: {duration:.2f}s"
            self._logger.success(msg)
        else:
            self._logger.error("❌ Task failed")


# Create a default logger instance
default_logger = get_logger("local-agent")