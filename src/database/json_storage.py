"""
Simple JSON file-based storage as fallback when MongoDB is not available
"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class JSONStorage:
    """Simple JSON file storage for YouTube data when MongoDB is unavailable"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.videos_file = os.path.join(data_dir, "videos.json")
        self.channels_file = os.path.join(data_dir, "channels.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files with empty data if they don't exist"""
        if not os.path.exists(self.videos_file):
            with open(self.videos_file, 'w') as f:
                json.dump([], f)
        
        if not os.path.exists(self.channels_file):
            with open(self.channels_file, 'w') as f:
                json.dump([], f)
    
    def _load_videos(self) -> List[Dict]:
        """Load videos from JSON file"""
        try:
            with open(self.videos_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_videos(self, videos: List[Dict]):
        """Save videos to JSON file"""
        try:
            with open(self.videos_file, 'w') as f:
                json.dump(videos, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving videos: {e}")
    
    def insert_video(self, video_data: Dict) -> bool:
        """Insert a video (avoid duplicates by video_id)"""
        try:
            videos = self._load_videos()
            
            # Check if video already exists
            video_id = video_data.get('video_id')
            if any(v.get('video_id') == video_id for v in videos):
                return False  # Already exists
            
            # Add timestamp
            video_data['created_at'] = datetime.now().isoformat()
            
            videos.append(video_data)
            self._save_videos(videos)
            return True
        except Exception as e:
            logger.error(f"Error inserting video: {e}")
            return False
    
    def get_video_count_by_channel(self, channel_name: str) -> int:
        """Get count of videos for a specific channel"""
        try:
            videos = self._load_videos()
            count = sum(1 for v in videos if v.get('channel_name', '').lower() == channel_name.lower())
            return count
        except:
            return 0
    
    def get_all_videos(self) -> List[Dict]:
        """Get all videos"""
        return self._load_videos()
    
    def get_channel_stats(self) -> Dict[str, int]:
        """Get video count per channel"""
        try:
            videos = self._load_videos()
            stats = {}
            for video in videos:
                channel = video.get('channel_name', 'Unknown')
                stats[channel] = stats.get(channel, 0) + 1
            return stats
        except:
            return {}