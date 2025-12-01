"""
Main FastAPI application - No AWS dependencies
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging
from datetime import datetime

from src.database.mongodb_client import MongoDBClient
from src.database.models import VideoMetadata
from src.utils.auth import verify_api_key
from src.utils.config import get_settings
from .webhook import router as webhook_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Monitoring API",
    description="Real-time YouTube video monitoring system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook_router)

# Initialize database client
db_client = MongoDBClient()

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint"""
    return {
        "message": "YouTube Real-Time Monitoring System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_client.get_recent_videos(1)
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "disconnected",
                "error": str(e)
            }
        )

@app.get("/videos/recent", response_model=List[VideoMetadata])
async def get_recent_videos(
    limit: int = Query(10, ge=1, le=100, description="Number of recent videos to fetch"),
    channel_id: Optional[str] = Query(None, description="Filter by channel ID"),
    api_key: str = Depends(verify_api_key)
):
    """Get most recent videos from database"""
    try:
        videos = db_client.get_recent_videos(limit, channel_id)
        return videos
    except Exception as e:
        logger.error(f"Error fetching recent videos: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/videos/channel/{channel_id}", response_model=List[VideoMetadata])
async def get_videos_by_channel(
    channel_id: str,
    limit: int = Query(50, ge=1, le=200, description="Number of videos to fetch"),
    api_key: str = Depends(verify_api_key)
):
    """Get videos by channel ID"""
    try:
        videos = db_client.get_videos_by_channel(channel_id, limit)
        if not videos:
            raise HTTPException(status_code=404, detail="No videos found for this channel")
        return videos
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching channel videos: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/stats/channel/{channel_id}")
async def get_channel_stats(
    channel_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get statistics for a channel"""
    try:
        stats = db_client.get_channel_stats(channel_id)
        video_count = db_client.get_video_count_by_channel(channel_id)
        recent_videos = db_client.get_recent_videos(5, channel_id)
        
        return {
            "channel_id": channel_id,
            "total_videos": video_count,
            "statistics": stats,
            "recent_videos": recent_videos
        }
    except Exception as e:
        logger.error(f"Error fetching channel stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/search/videos")
async def search_videos(
    query: str = Query(..., description="Search query for title and description"),
    channel_id: Optional[str] = Query(None, description="Filter by channel ID"),
    hours: Optional[int] = Query(None, ge=1, description="Filter by last N hours"),
    api_key: str = Depends(verify_api_key)
):
    """Search videos by text in title and description"""
    try:
        videos = db_client.search_videos(query, channel_id, hours)
        return {
            "query": query,
            "channel_id": channel_id,
            "time_frame_hours": hours,
            "results_count": len(videos),
            "videos": videos
        }
    except Exception as e:
        logger.error(f"Error searching videos: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/channels")
async def get_monitored_channels(api_key: str = Depends(verify_api_key)):
    """Get list of monitored channels"""
    from src.youtube.channel_manager import ChannelManager
    channel_manager = ChannelManager()
    
    channels = channel_manager.get_all_channels()
    return {
        "channels": [
            {
                "channel_id": channel.channel_id,
                "handle": channel.handle,
                "name": channel.name,
                "description": channel.description,
                "timezone": channel.timezone
            }
            for channel in channels
        ]
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )