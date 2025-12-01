"""
Initial data ingestion script - No AWS dependencies
"""
import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.youtube.data_extractor import YouTubeDataExtractor
from src.database.mongodb_client import MongoDBClient
from src.database.models import VideoMetadata
from src.youtube.channel_manager import ChannelManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main data ingestion function"""
    logger.info("🚀 Starting initial data ingestion...")
    
    extractor = YouTubeDataExtractor()
    db_client = MongoDBClient()
    channel_manager = ChannelManager()
    
    # Extract data from all channels
    all_videos = await extractor.extract_all_channel_data(max_results=100)
    
    logger.info(f"📥 Extracted {len(all_videos)} videos total")
    
    # Store videos in database
    successful_inserts = 0
    for video_data in all_videos:
        if video_data:
            try:
                video_metadata = VideoMetadata(**video_data)
                success = db_client.insert_video(video_metadata)
                if success:
                    successful_inserts += 1
            except Exception as e:
                logger.error(f"Error inserting video {video_data.get('video_id')}: {e}")
    
    logger.info(f"✅ Successfully stored {successful_inserts} videos in database")
    
    # Display summary
    channels = channel_manager.get_all_channels()
    for channel in channels:
        count = db_client.get_video_count_by_channel(channel.channel_id)
        logger.info(f"📊 {channel.name}: {count} videos")

if __name__ == "__main__":
    asyncio.run(main())