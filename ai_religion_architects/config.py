import os
from typing import Optional
from pathlib import Path
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)


class Config:
    """Configuration management for AI Religion Architects with Claude API integration"""
    
    # Claude API Configuration
    CLAUDE_API_KEY: Optional[str] = os.getenv("CLAUDE_API_KEY")
    CLAUDE_API_URL: str = "https://api.anthropic.com/v1/messages"
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    CLAUDE_MAX_TOKENS: int = int(os.getenv("CLAUDE_MAX_TOKENS", "2000"))
    CLAUDE_TEMPERATURE: float = float(os.getenv("CLAUDE_TEMPERATURE", "0.7"))
    
    # Rate Limiting Configuration
    CYCLE_INTERVAL_HOURS: int = int(os.getenv("CYCLE_INTERVAL_HOURS", "1"))
    CYCLE_INTERVAL_SECONDS: int = CYCLE_INTERVAL_HOURS * 3600
    
    # Retry Configuration
    API_RETRY_COUNT: int = int(os.getenv("API_RETRY_COUNT", "3"))
    API_RETRY_DELAY: float = float(os.getenv("API_RETRY_DELAY", "1.0"))
    API_RETRY_BACKOFF: float = float(os.getenv("API_RETRY_BACKOFF", "2.0"))
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "60"))
    
    # Database Configuration
    DB_PATH: str = os.getenv("DB_PATH", "data/religion_memory.db")
    
    # Logging Configuration
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    API_ERROR_LOG: str = os.getenv("API_ERROR_LOG", "api_errors.log")
    
    # WebSocket Configuration
    WEBSOCKET_URL: str = os.getenv("WEBSOCKET_URL", "http://localhost:8000")
    WEBSOCKET_PORT: int = int(os.getenv("WEBSOCKET_PORT", "8000"))
    
    # Security Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration values"""
        errors = []
        
        if not cls.CLAUDE_API_KEY:
            errors.append("CLAUDE_API_KEY environment variable is required")
        
        if not cls.CLAUDE_API_KEY or not cls.CLAUDE_API_KEY.startswith("sk-ant-api"):
            errors.append("CLAUDE_API_KEY must be a valid Anthropic API key (starts with 'sk-ant-api')")
        
        if cls.CLAUDE_MAX_TOKENS < 100 or cls.CLAUDE_MAX_TOKENS > 4000:
            errors.append("CLAUDE_MAX_TOKENS must be between 100 and 4000")
        
        if cls.CYCLE_INTERVAL_HOURS < 1:
            errors.append("CYCLE_INTERVAL_HOURS must be at least 1")
        
        if cls.API_RETRY_COUNT < 1 or cls.API_RETRY_COUNT > 10:
            errors.append("API_RETRY_COUNT must be between 1 and 10")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            return False
        
        return True
    
    @classmethod
    def setup_logging(cls):
        """Setup logging configuration"""
        # Create logs directory
        log_dir = Path(cls.LOG_DIR)
        log_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_dir / "ai_religion_architects.log")
            ]
        )
        
        # Configure API error logger
        api_error_logger = logging.getLogger('api_errors')
        api_error_handler = logging.FileHandler(log_dir / cls.API_ERROR_LOG)
        api_error_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        api_error_logger.addHandler(api_error_handler)
        api_error_logger.setLevel(logging.ERROR)
    
    @classmethod
    def load_env_file(cls, env_file_path: str = ".env"):
        """Load environment variables from .env file"""
        env_path = Path(env_file_path)
        if env_path.exists():
            try:
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            os.environ.setdefault(key.strip(), value.strip())
                logger.info(f"Loaded environment variables from {env_path}")
            except Exception as e:
                logger.warning(f"Failed to load .env file: {e}")
        else:
            logger.info(f"No .env file found at {env_path}")
    
    @classmethod
    def get_summary(cls) -> dict:
        """Get a summary of current configuration (without sensitive data)"""
        return {
            "claude_model": cls.CLAUDE_MODEL,
            "claude_max_tokens": cls.CLAUDE_MAX_TOKENS,
            "claude_temperature": cls.CLAUDE_TEMPERATURE,
            "cycle_interval_hours": cls.CYCLE_INTERVAL_HOURS,
            "api_retry_count": cls.API_RETRY_COUNT,
            "api_timeout": cls.API_TIMEOUT,
            "db_path": cls.DB_PATH,
            "log_level": cls.LOG_LEVEL,
            "environment": cls.ENVIRONMENT,
            "debug": cls.DEBUG,
            "api_key_configured": bool(cls.CLAUDE_API_KEY),
        }


# Initialize configuration
def init_config():
    """Initialize configuration and logging"""
    # Load .env file first
    Config.load_env_file()
    
    # Setup logging
    Config.setup_logging()
    
    # Validate configuration
    if not Config.validate():
        raise ValueError("Configuration validation failed. Check logs for details.")
    
    logger.info("Configuration initialized successfully")
    logger.info(f"Config summary: {Config.get_summary()}")


# Export the Config class
__all__ = ["Config", "init_config"]