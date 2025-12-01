"""
MongoDB client with connection management and operations
"""
import os
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from typing import List, Optional, Dict, Any
import logging
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import VideoMetadata, ChannelInfo
from utils.config import get_settings

logger = logging.getLogger(__name__)

class MongoDBClient:
    """MongoDB client for YouTube video data"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.settings = get_settings()
        self.client = None
        self.db = None
        self.collection = None
        self.channels_collection = None
        
        self._connect()
        self._initialized = True
    
    def _connect(self):
        """Establish MongoDB connection"""
        try:
            mongodb_uri = self.settings.effective_mongodb_uri
            self.client = MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            self.db = self.client[self.settings.database_name]
            self.collection = self.db["videos"]
            self.channels_collection = self.db["channels"]
            
            # Create indexes
            self._create_indexes()
            
            logger.info("✅ Successfully connected to MongoDB")
            
        except ConnectionFailure as e:
            error_msg = f"❌ MongoDB connection failed: {e}"
            if "localhost" in mongodb_uri:
                error_msg += "\n💡 For Streamlit Cloud deployment, you need to use MongoDB Atlas instead of localhost. Please configure MONGODB_URI in Streamlit secrets."
            logger.error(error_msg)
            raise ConnectionFailure(error_msg)
        except Exception as e:
            error_msg = f"❌ Unexpected MongoDB error: {e}"
            logger.error(error_msg)
            raise
    
    def _create_indexes(self):
        """Create necessary database indexes"""
        # Unique index for video_id to ensure idempotency
        self.collection.create_index("video_id", unique=True, background=True)
        
        # Compound indexes for common queries
        self.collection.create_index([("channel_id", 1), ("upload_date", -1)], background=True)
        self.collection.create_index([("upload_date", -1)], background=True)
        self.collection.create_index([("title", "text"), ("description", "text")], background=True)
        
        # Channel indexes
        self.channels_collection.create_index("channel_id", unique=True, background=True)
        self.channels_collection.create_index("is_monitored", background=True)
    
    def insert_video(self, video_data: VideoMetadata) -> bool:
        """
        Insert video metadata with idempotency
        Returns True if successful, False if duplicate
        """
        try:
            result = self.collection.insert_one(video_data.dict())
            logger.info(f"✅ Inserted video: {video_data.video_id}")
            return result.acknowledged
            
        except DuplicateKeyError:
            logger.info(f"⚠️ Video already exists: {video_data.video_id}")
            return True  # Consider duplicate as success for idempotency
            
        except Exception as e:
            logger.error(f"❌ Error inserting video {video_data.video_id}: {e}")
            return False
    
    def get_recent_videos(self, limit: int = 10, channel_id: Optional[str] = None) -> List[Dict]:
        """Get most recent videos, optionally filtered by channel"""
        query = {}
        if channel_id:
            query["channel_id"] = channel_id
            
        return list(self.collection.find(query)
                   .sort("upload_date", -1)
                   .limit(limit))
    
    def get_videos_by_channel(self, channel_id: str, limit: int = 50) -> List[Dict]:
        """Get videos by channel ID"""
        return list(self.collection.find({"channel_id": channel_id})
                   .sort("upload_date", -1)
                   .limit(limit))
    
    def get_video_count_by_channel(self, channel_id: str) -> int:
        """Get count of videos for a channel"""
        return self.collection.count_documents({"channel_id": channel_id})
    
    def search_videos(self, query: str, channel_id: Optional[str] = None, 
                     hours: Optional[int] = None) -> List[Dict]:
        """Search videos by text in title and description with optional filters"""
        from datetime import datetime, timedelta
        
        search_filter = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]
        }
        
        if channel_id:
            search_filter["channel_id"] = channel_id
            
        if hours:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            search_filter["upload_date"] = {"$gte": cutoff_time.isoformat()}
        
        return list(self.collection.find(search_filter)
                   .sort("upload_date", -1)
                   .limit(100))
    
    def get_channel_stats(self, channel_id: str) -> Dict[str, Any]:
        """Get statistics for a channel"""
        pipeline = [
            {"$match": {"channel_id": channel_id}},
            {"$group": {
                "_id": "$channel_id",
                "total_videos": {"$sum": 1},
                "total_views": {"$sum": "$view_count"},
                "total_likes": {"$sum": "$like_count"},
                "average_views": {"$avg": "$view_count"},
                "average_likes": {"$avg": "$like_count"},
                "latest_upload": {"$max": "$upload_date"}
            }}
        ]
        
        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else {}
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("🔌 MongoDB connection closed")