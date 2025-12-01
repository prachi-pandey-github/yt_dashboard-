"""
Utility functions and helpers
"""
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from urllib.parse import urlencode

def generate_video_hash(video_data: Dict[str, Any]) -> str:
    """Generate unique hash for video data to ensure idempotency"""
    hash_string = f"{video_data['video_id']}_{video_data['channel_id']}"
    return hashlib.md5(hash_string.encode()).hexdigest()

def validate_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """Validate webhook signature"""
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha1
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

def parse_iso_date(date_string: str) -> Optional[datetime]:
    """Parse ISO date string with multiple format support"""
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d",
        "%Y%m%d"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    return None

def build_youtube_search_url(params: Dict[str, Any]) -> str:
    """Build YouTube search URL with parameters"""
    base_url = "https://www.youtube.com/results"
    return f"{base_url}?{urlencode(params)}"

def format_duration(seconds: int) -> str:
    """Format duration in seconds to HH:MM:SS"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"