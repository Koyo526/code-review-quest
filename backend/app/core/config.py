"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://crq_user:crq_password@localhost:5432/code_review_quest"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_EXPIRE_SECONDS: int = 3600
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000",
    ]
    
    # Trusted hosts
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Code analysis
    CODE_EXECUTION_TIMEOUT: int = 30
    MAX_CODE_LENGTH: int = 10000
    ALLOWED_IMPORTS: List[str] = [
        "os", "sys", "json", "math", "random", "datetime", "collections",
        "itertools", "functools", "operator", "re", "string", "typing"
    ]
    
    # Game settings
    DEFAULT_TIME_LIMIT: int = 900  # 15 minutes in seconds
    MIN_TIME_LIMIT: int = 300      # 5 minutes
    MAX_TIME_LIMIT: int = 1800     # 30 minutes
    
    # Scoring
    BASE_SCORE: int = 100
    TIME_BONUS_MULTIPLIER: float = 1.5
    DIFFICULTY_MULTIPLIERS: dict = {
        "beginner": 1.0,
        "intermediate": 1.5,
        "advanced": 2.0
    }
    
    # External services
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # File storage
    UPLOAD_DIR: str = "/tmp/uploads"
    MAX_UPLOAD_SIZE: int = 1024 * 1024  # 1MB
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # Worker settings
    WORKER_CONCURRENCY: int = 4
    TASK_TIMEOUT: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Validate critical settings
def validate_settings():
    """Validate critical application settings"""
    errors = []
    
    if settings.ENVIRONMENT == "production":
        if settings.SECRET_KEY == "your-secret-key-change-in-production":
            errors.append("SECRET_KEY must be changed in production")
        
        if settings.JWT_SECRET_KEY == "your-jwt-secret-key-change-in-production":
            errors.append("JWT_SECRET_KEY must be changed in production")
        
        if settings.DEBUG:
            errors.append("DEBUG should be False in production")
    
    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL is required")
    
    if not settings.REDIS_URL:
        errors.append("REDIS_URL is required")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")


# Validate on import
validate_settings()
