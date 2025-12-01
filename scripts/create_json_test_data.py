"""
Populate JSON storage with test data when MongoDB is not available
"""
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from database.json_storage import JSONStorage
from datetime import datetime, timedelta
import random

def create_test_data():
    """Create test YouTube video data"""
    storage = JSONStorage()
    
    # Bloomberg Markets test data
    bloomberg_videos = []
    for i in range(20):
        video = {
            "video_id": f"bloomberg_test_{i+1}",
            "title": f"Bloomberg Markets Test Video {i+1}",
            "description": f"Test video {i+1} from Bloomberg Markets channel",
            "channel_id": "UCIALMKvObZNtJ6AmdCLP7Lg",
            "channel_name": "markets",
            "upload_date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "duration": f"PT{random.randint(5, 15)}M{random.randint(0, 59)}S",
            "view_count": random.randint(10000, 100000),
            "like_count": random.randint(500, 5000),
            "comment_count": random.randint(50, 500),
            "tags": ["finance", "markets", "bloomberg", "news"]
        }
        bloomberg_videos.append(video)
        storage.insert_video(video)
    
    # ANI News test data
    ani_videos = []
    for i in range(10):
        video = {
            "video_id": f"ani_test_{i+1}",
            "title": f"ANI News Test Video {i+1}",
            "description": f"Test video {i+1} from ANI News channel",
            "channel_id": "UCUQTWRcglE3gX3kw3MhDbNg",
            "channel_name": "aninewsindia",
            "upload_date": (datetime.now() - timedelta(days=random.randint(1, 20))).isoformat(),
            "duration": f"PT{random.randint(2, 8)}M{random.randint(0, 59)}S",
            "view_count": random.randint(5000, 50000),
            "like_count": random.randint(200, 2000),
            "comment_count": random.randint(20, 200),
            "tags": ["news", "india", "ani", "current affairs"]
        }
        ani_videos.append(video)
        storage.insert_video(video)
    
    print(f"✅ Created test data:")
    print(f"   - Bloomberg Markets: {len(bloomberg_videos)} videos")
    print(f"   - ANI News: {len(ani_videos)} videos")
    print(f"   - Total: {len(bloomberg_videos) + len(ani_videos)} videos")
    
    # Test the queries
    print(f"\n📊 Test queries:")
    print(f"   - markets videos: {storage.get_video_count_by_channel('markets')}")
    print(f"   - aninewsindia videos: {storage.get_video_count_by_channel('aninewsindia')}")
    print(f"   - Channel stats: {storage.get_channel_stats()}")

if __name__ == "__main__":
    create_test_data()