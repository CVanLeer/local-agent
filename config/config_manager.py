"""Configuration management system"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from dotenv import load_dotenv
from utils.logging import get_logger


@dataclass
class AgentConfig:
    """Agent-specific configuration"""
    model: str = "ollama/qwen2.5-coder:14b-instruct-q4_K_M"
    context_window: int = 32000
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 300
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class SystemConfig:
    """System-wide configuration"""
    log_level: str = "INFO"
    log_dir: str = "logs"
    cache_dir: str = ".cache"
    data_dir: str = "data"
    enable_telemetry: bool = False
    max_workers: int = 4
    api_port: int = 8000
    api_host: str = "0.0.0.0"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    database: str = "agent_system"
    username: str = ""
    password: str = ""
    pool_size: int = 10
    pool_timeout: int = 30


@dataclass
class RedisConfig:
    """Redis configuration for caching/queue"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str = ""
    max_connections: int = 50
    socket_timeout: int = 5
    connection_timeout: int = 5


@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_auth: bool = False
    api_key: str = ""
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    allowed_origins: list = field(default_factory=lambda: ["*"])
    rate_limit_per_minute: int = 60


@dataclass
class AppConfig:
    """Main application configuration"""
    agent: AgentConfig = field(default_factory=AgentConfig)
    system: SystemConfig = field(default_factory=SystemConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """Create config from dictionary"""
        agent_data = data.get('agent', {})
        system_data = data.get('system', {})
        database_data = data.get('database', {})
        redis_data = data.get('redis', {})
        security_data = data.get('security', {})
        
        return cls(
            agent=AgentConfig(**agent_data),
            system=SystemConfig(**system_data),
            database=DatabaseConfig(**database_data),
            redis=RedisConfig(**redis_data),
            security=SecurityConfig(**security_data)
        )


class ConfigManager:
    """Manages application configuration from multiple sources"""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file (yaml or json)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.config_path = Path(config_path) if config_path else None
        self.config = AppConfig()
        
        # Load configuration in order of precedence
        self._load_defaults()
        self._load_file()
        self._load_env()
        
    def _load_defaults(self) -> None:
        """Load default configuration"""
        self.config = AppConfig()
        self.logger.debug("Loaded default configuration")
        
    def _load_file(self) -> None:
        """Load configuration from file"""
        # Try multiple locations
        search_paths = []
        
        if self.config_path:
            search_paths.append(self.config_path)
        
        search_paths.extend([
            Path("config.yaml"),
            Path("config.yml"),
            Path("config.json"),
            Path(".env.yaml"),
            Path(".env.json"),
            Path.home() / ".local-agent" / "config.yaml",
            Path("/etc/local-agent/config.yaml")
        ])
        
        for path in search_paths:
            if path.exists():
                try:
                    if path.suffix in ['.yaml', '.yml']:
                        with open(path, 'r') as f:
                            data = yaml.safe_load(f)
                    elif path.suffix == '.json':
                        with open(path, 'r') as f:
                            data = json.load(f)
                    else:
                        continue
                    
                    if data:
                        self.config = AppConfig.from_dict(data)
                        self.logger.info(f"Loaded configuration from {path}")
                        break
                        
                except Exception as e:
                    self.logger.warning(f"Failed to load config from {path}: {e}")
                    
    def _load_env(self) -> None:
        """Load configuration from environment variables"""
        # Load .env file if exists
        load_dotenv()
        
        # Override with environment variables
        # Format: AGENT_<SECTION>_<KEY>
        
        # Agent config
        if env_model := os.getenv("AGENT_MODEL"):
            self.config.agent.model = env_model
        if env_tokens := os.getenv("AGENT_MAX_TOKENS"):
            self.config.agent.max_tokens = int(env_tokens)
        if env_temp := os.getenv("AGENT_TEMPERATURE"):
            self.config.agent.temperature = float(env_temp)
            
        # System config
        if env_log_level := os.getenv("AGENT_LOG_LEVEL"):
            self.config.system.log_level = env_log_level
        if env_log_dir := os.getenv("AGENT_LOG_DIR"):
            self.config.system.log_dir = env_log_dir
        if env_port := os.getenv("AGENT_API_PORT"):
            self.config.system.api_port = int(env_port)
            
        # Database config
        if env_db_host := os.getenv("AGENT_DB_HOST"):
            self.config.database.host = env_db_host
        if env_db_port := os.getenv("AGENT_DB_PORT"):
            self.config.database.port = int(env_db_port)
        if env_db_name := os.getenv("AGENT_DB_NAME"):
            self.config.database.database = env_db_name
        if env_db_user := os.getenv("AGENT_DB_USER"):
            self.config.database.username = env_db_user
        if env_db_pass := os.getenv("AGENT_DB_PASSWORD"):
            self.config.database.password = env_db_pass
            
        # Redis config
        if env_redis_host := os.getenv("AGENT_REDIS_HOST"):
            self.config.redis.host = env_redis_host
        if env_redis_port := os.getenv("AGENT_REDIS_PORT"):
            self.config.redis.port = int(env_redis_port)
        if env_redis_pass := os.getenv("AGENT_REDIS_PASSWORD"):
            self.config.redis.password = env_redis_pass
            
        # Security config
        if env_api_key := os.getenv("AGENT_API_KEY"):
            self.config.security.api_key = env_api_key
        if env_jwt_secret := os.getenv("AGENT_JWT_SECRET"):
            self.config.security.jwt_secret = env_jwt_secret
            
        self.logger.debug("Loaded environment variable overrides")
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot notation
        
        Args:
            key: Dot-separated key (e.g., 'agent.model')
            default: Default value if key not found
        """
        parts = key.split('.')
        value = self.config
        
        try:
            for part in parts:
                if hasattr(value, part):
                    value = getattr(value, part)
                else:
                    return default
            return value
        except:
            return default
            
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by dot notation
        
        Args:
            key: Dot-separated key (e.g., 'agent.model')
            value: Value to set
        """
        parts = key.split('.')
        
        if len(parts) < 2:
            raise ValueError(f"Invalid configuration key: {key}")
            
        section = parts[0]
        attr = parts[1]
        
        if hasattr(self.config, section):
            section_obj = getattr(self.config, section)
            if hasattr(section_obj, attr):
                setattr(section_obj, attr, value)
                self.logger.debug(f"Set {key} = {value}")
            else:
                raise ValueError(f"Unknown configuration attribute: {attr}")
        else:
            raise ValueError(f"Unknown configuration section: {section}")
            
    def save(self, path: Optional[Union[str, Path]] = None) -> None:
        """
        Save configuration to file
        
        Args:
            path: Path to save configuration
        """
        save_path = Path(path) if path else self.config_path
        
        if not save_path:
            save_path = Path("config.yaml")
            
        data = self.config.to_dict()
        
        if save_path.suffix in ['.yaml', '.yml']:
            with open(save_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        elif save_path.suffix == '.json':
            with open(save_path, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported file format: {save_path.suffix}")
            
        self.logger.info(f"Saved configuration to {save_path}")
        
    def reload(self) -> None:
        """Reload configuration from sources"""
        self._load_defaults()
        self._load_file()
        self._load_env()
        self.logger.info("Configuration reloaded")


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager