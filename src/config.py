"""Configuration management"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_reload: bool = False
    
    # Redis Settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    session_ttl_hours: int = 24
    
    # Model Settings
    artifacts_path: str = "src/artifacts"
    model_version: str = "latest"
    model_s3_bucket: Optional[str] = None
    
    # Recommendation Settings
    default_k: int = 20
    max_k: int = 100
    candidate_pool_size: int = 100
    min_similarity_threshold: float = 0.1
    diversity_weight: float = 0.3
    
    # Feature Engineering
    enable_temporal_features: bool = True
    enable_similarity_features: bool = True
    session_window_size: int = 50
    
    # Performance
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    rate_limit_per_minute: int = 1000
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    enable_request_logging: bool = True
    
    # Monitoring
    enable_metrics: bool = False
    metrics_port: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
