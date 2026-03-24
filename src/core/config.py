from pydantic_settings import BaseSettings
from typing import Optional, List
from enum import Enum


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Platform(str, Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    MEDIUM = "medium"


class Settings(BaseSettings):
    # OpenRouter Configuration
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_llm_model: str = "anthropic/claude-3-sonnet"
    
    # Platform API Keys
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None
    linkedin_access_token: Optional[str] = None
    
    medium_integration_token: Optional[str] = None
    
    # Database Configuration
    database_url: str = "sqlite:///./content_machine.db"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Application Settings
    debug: bool = False
    log_level: LogLevel = LogLevel.INFO
    secret_key: str
    
    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Content Settings
    max_content_length: int = 5000
    human_review_required: bool = True
    
    # Platform-specific limits
    twitter_max_length: int = 280
    linkedin_max_length: int = 3000
    medium_min_length: int = 800
    medium_max_length: int = 2000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
