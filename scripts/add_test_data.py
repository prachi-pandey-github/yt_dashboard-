"""
Add test data to the database for testing purposes
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.mongodb_client import MongoDBClient
from src.database.models import VideoMetadata

def create_test_video(channel_id: str, channel_name: str, video_num: int) -> VideoMetadata:
    """Create a test video metadata object"""
    base_date = datetime.now() - timedelta(days=video_num)
    
    return VideoMetadata(
        video_id=f"test_video_{video_num}_{channel_name.replace(' ', '_')}",
        title=f"Test Video {video_num} from {channel_name}",
        url=f"https://www.youtube.com/watch?v=test_video_{video_num}",
        upload_date=base_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        description=f"This is test video number {video_num} from {channel_name} channel",
        channel_id=channel_id,
        channel_title=channel_name,
        view_count=random.randint(1000, 100000),
        like_count=random.randint(10, 1000),
        tags=["test", "youtube", "data"],
        category="news",
        thumbnail_url=f"https://example.com/thumbnail_{video_num}.jpg"
    )

def main():
    """Add test data to database"""
    print("🚀 Adding test data to database...")
    
    db_client = MongoDBClient()
    
    # Test data for Bloomberg Markets
    bloomberg_channel_id = "UCaIGZ2lNpryhA-p9KXr5XNw"
    
    print("📥 Adding test videos for Bloomberg Markets...")
    for i in range(1, 21):  # Add 20 test videos
        video = create_test_video(bloomberg_channel_id, "Bloomberg Markets", i)
        success = db_client.insert_video(video)
        if success:
            print(f"✅ Added test video {i}")
        else:
            print(f"❌ Failed to add test video {i}")
    
    # Test data for ANI News
    ani_channel_id = "UCUDXkpsJIdv1aKb1TCN2p0Q"
    
    print("📥 Adding test videos for ANI News...")
    for i in range(1, 11):  # Add 10 test videos
        video = create_test_video(ani_channel_id, "ANI News India", i)
        success = db_client.insert_video(video)
        if success:
            print(f"✅ Added ANI test video {i}")
        else:
            print(f"❌ Failed to add ANI test video {i}")
    
    # Check final counts
    bloomberg_count = db_client.get_video_count_by_channel(bloomberg_channel_id)
    ani_count = db_client.get_video_count_by_channel(ani_channel_id)
    
    print(f"\n📊 Final counts:")
    print(f"Bloomberg Markets: {bloomberg_count} videos")
    print(f"ANI News India: {ani_count} videos")
    print("✅ Test data addition complete!")

if __name__ == "__main__":
    main()