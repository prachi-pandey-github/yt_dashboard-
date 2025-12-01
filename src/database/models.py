"""
Data models for YouTube video metadata
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class VideoCategory(str, Enum):
    NEWS = "news"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    TECHNOLOGY = "technology"
    SPORTS = "sports"
    OTHER = "other"

class VideoMetadata(BaseModel):
    """YouTube video metadata model"""
    video_id: str = Field(..., description="Unique YouTube video ID")
    title: str = Field(..., description="Video title", max_length=500)
    url: str = Field(..., description="Full YouTube video URL")
    upload_date: str = Field(..., description="ISO 8601 upload date")
    view_count: int = Field(default=0, ge=0, description="View count")
    like_count: int = Field(default=0, ge=0, description="Like count")
    description: str = Field(default="", description="Video description")
    channel_id: str = Field(..., description="YouTube channel ID")
    channel_title: str = Field(..., description="Channel title")
    thumbnail_url: str = Field(default="", description="Thumbnail URL")
    duration: Optional[str] = Field(default=None, description="Video duration")
    tags: List[str] = Field(default_factory=list, description="Video tags")
    category_id: Optional[str] = Field(default=None, description="YouTube category ID")
    category: Optional[VideoCategory] = Field(default=VideoCategory.OTHER, description="Content category")
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="When record was processed")
    
    @validator('upload_date')
    def validate_upload_date(cls, v):
        """Validate upload date format"""
        from src.utils.helpers import parse_iso_date
        if parse_iso_date(v) is None:
            raise ValueError('Invalid date format. Use ISO 8601 format.')
        return v
    
    @validator('title', 'description')
    def sanitize_text(cls, v):
        """Basic text sanitization"""
        if v:
            # Remove extra whitespace
            v = ' '.join(v.split())
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "title": "Example Video Title",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "upload_date": "2023-12-01T12:00:00Z",
                "view_count": 1500,
                "like_count": 120,
                "description": "This is an example video description",
                "channel_id": "UC1234567890",
                "channel_title": "Example Channel",
                "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
                "duration": "10:30",
                "tags": ["example", "test", "demo"],
                "category_id": "22",
                "category": "education"
            }
        }

class ChannelInfo(BaseModel):
    """YouTube channel information"""
    channel_id: str
    channel_handle: str
    channel_title: str
    description: str = ""
    subscriber_count: int = 0
    video_count: int = 0
    is_monitored: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)