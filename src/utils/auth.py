"""
Authentication utilities
"""
from fastapi import HTTPException, Header, status
from typing import List
from src.utils.config import get_settings

def verify_api_key(api_key: str = Header(None, alias="X-API-Key")) -> str:
    """Verify API key from request header"""
    settings = get_settings()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    if api_key not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return api_key

def get_api_keys() -> List[str]:
    """Get valid API keys"""
    return get_settings().api_keys