"""
Configuration management using Pydantic settings - No AWS dependencies
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache
import os
import streamlit as st

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
    gemini_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Deployment Platforms (Optional)
    railway_api_key: Optional[str] = None
    render_api_key: Optional[str] = None
    
    def get_secret(self, key: str, default: any = None):
        """Get secret from Streamlit secrets or environment variable"""
        try:
            # Try Streamlit secrets first (for cloud deployment)
            import streamlit as st
            if hasattr(st, 'secrets') and key in st.secrets:
                return st.secrets[key]
        except ImportError:
            # Streamlit not available (local development)
            pass
        except Exception:
            # Streamlit available but secrets not configured
            pass
        
        # Fall back to environment variable
        return os.getenv(key, default)
    
    @property
    def effective_mongodb_uri(self) -> str:
        """Get MongoDB URI from secrets or config"""
        return self.get_secret('MONGODB_URI', self.mongodb_uri)
    
    @property 
    def effective_youtube_api_key(self) -> Optional[str]:
        """Get YouTube API key from secrets or config"""
        return self.get_secret('YOUTUBE_API_KEY', self.youtube_api_key)
    
    @property
    def effective_gemini_api_key(self) -> Optional[str]:
        """Get Gemini API key from secrets or config"""
        return self.get_secret('GEMINI_API_KEY', self.gemini_api_key)
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()