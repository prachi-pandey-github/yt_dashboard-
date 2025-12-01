"""
Configuration management using Pydantic settings - No AWS dependencies
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings - Cloud agnostic"""
    
    # Application
    app_name: str = "YouTube Monitoring System"
    environment: str = "development"
    port: int = 8000
    debug: bool = True
    
    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017/"
    database_name: str = "youtube_monitoring"
    
    # YouTube API
    youtube_api_key: Optional[str] = None
    
    # Webhook
    webhook_base_url: str = "http://localhost:8000"
    webhook_verify_token: str = "youtube_verify_token"
    webhook_secret: str = "youtube_webhook_secret"
    
    # API Security
    api_keys: List[str] = ["test-key-123"]
    jwt_secret: str = "your-jwt-secret-key"
    
    # AI/ML - Optional
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Deployment Platforms (Optional)
    railway_api_key: Optional[str] = None
    render_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()